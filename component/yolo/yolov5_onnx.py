import cv2
import numpy as np
import torch
from torchvision.ops import nms
from PIL import Image, ImageOps
import threading
import time
import onnxruntime as ort
from component.action.ActionManager import actionManager


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - \
        new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / \
            shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right,
                            cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)


def resize_img(im):
    target_size = 640   # 目标尺寸
    width, height = im.size
    if width < height:
        new_height = target_size
        new_width = int(new_height / height * width)
    else:
        new_width = target_size
        new_height = int(new_width / width * height)
    resized_im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
    pad_width = target_size - new_width
    pad_height = target_size - new_height

    # 计算每边需要补的像素数
    left_pad = pad_width // 2
    right_pad = pad_width - left_pad
    top_pad = pad_height // 2
    bottom_pad = pad_height - top_pad
    # print(top_pad,top_pad)
    # 补hui色边
    new_im = ImageOps.expand(resized_im, border=(left_pad, top_pad, right_pad, bottom_pad), fill=(114, 114, 114))

    return new_im, top_pad


def from_numpy(x):
    """Converts a NumPy array to a torch tensor, maintaining device compatibility."""
    return torch.from_numpy(x) if isinstance(x, np.ndarray) else x


def box_iou(box1, box2, eps=1e-7):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.

    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    (a1, a2), (b1, b2) = box1.unsqueeze(1).chunk(2, 2), box2.unsqueeze(0).chunk(2, 2)
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp(0).prod(2)

    # IoU = inter / (area1 + area2 - inter)
    return inter / ((a2 - a1).prod(2) + (b2 - b1).prod(2) - inter + eps)


def xywh2xyxy(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right."""
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    y[..., 2] = x[..., 0] + x[..., 2] / 2  # bottom right x
    y[..., 3] = x[..., 1] + x[..., 3] / 2  # bottom right y
    return y


def xyxy2xywh(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right."""
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 2] = x[..., 2] - x[..., 0] / 2  # bottom right x
    y[..., 3] = x[..., 3] - x[..., 1] / 2  # bottom right y
    return y


def NonMaximumSuppression(
    prediction,
    conf_thres=0.15,
    iou_thres=0.45,
    classes=None,
    agnostic=False,
    multi_label=False,
    labels=(),
    max_det=300,
    nm=0,  # number of masks
):
    """
    Non-Maximum Suppression (NMS) on inference results to reject overlapping detections.

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    # Checks
    assert 0 <= conf_thres <= 1, f"Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0"
    assert 0 <= iou_thres <= 1, f"Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0"
    if isinstance(prediction, (list, tuple)):  # YOLOv5 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output

    # print("xxxx1 shape",prediction.shape) #[1, 25200, 19]
    device = prediction.device
    mps = "mps" in device.type  # Apple MPS
    if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
        prediction = prediction.cpu()
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[2] - nm - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates
    # print("xc.shape",xc.shape)#[1, 25200]

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 0.5 + 0.05 * bs  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    mi = 5 + nc  # mask start index
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs

    # print("xxxx2 shape",prediction.shape) #[1, 25200, 19]

    m_i = 0
    s = time.time()
    for xi, x in enumerate(prediction):  # image index, image inference
        # print("xi",xi)#0
        # print("x.shape",x.shape)#[25200, 19]
        m_i = m_i+1
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        # print("xc.shape",xc.shape)#[1, 25200]
        # print("xc",xc)#[[False, False, False,  ..., False, False, False]]
        x = x[xc[xi]]  # confidence
        # print("x.shape",x.shape)#[191, 19]
        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box/Mask
        box = xywh2xyxy(x[:, :4])  # center_x, center_y, width, height) to (x1, y1, x2, y2)
        mask = x[:, mi:]  # zero columns if no masks

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:mi] > conf_thres).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, 5 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = x[:, 5:mi].max(1, keepdim=True)
            x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = nms(boxes, scores, iou_thres)  # NMS
        i = i[:max_det]  # limit detections
        if merge and (1 < n < 3e3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if mps:
            output[xi] = output[xi].to(device)

    # print(f'遍历耗时{int((time.time() - s) * 1000)} ms') #0
    # print("xxxx times:",m_i)#1
    # print("xxxx2 output",len(output))#1
    # print("xxxx2 output",len(output[0]))#9
    # print("xxxx2 output",len(output[0][0]))#6
    return output


def non_max_suppression(
    prediction,
    conf_thres=0.4,
    iou_thres=0.35,
    classes=None,
    agnostic=False,
    multi_label=False,
    labels=(),
    max_det=1000,
    nm=0,  # number of masks
):
    """
    Non-Maximum Suppression (NMS) on inference results to reject overlapping detections.

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    # Checks
    assert 0 <= conf_thres <= 1, f"Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0"
    assert 0 <= iou_thres <= 1, f"Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0"
    if isinstance(prediction, (list, tuple)):  # YOLOv5 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output
    device = prediction.device
    mps = "mps" in device.type  # Apple MPS
    if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
        prediction = prediction.cpu()
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[2] - nm - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates
    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 0.5 + 0.05 * bs  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    mi = 5 + nc  # mask start index
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence
        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        # x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box/Mask
        box = xywh2xyxy(x[:, :4])  # center_x, center_y, width, height) to (x1, y1, x2, y2)
        # box = x[:, :4]  # center_x, center_y, width, height) to (x1, y1, x2, y2)

        mask = x[:, 6:]  # zero columns if no masks

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:mi] > 0).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, 5 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = x[:, 5:mi].max(1, keepdim=True)
            x = torch.cat((box, x[..., 4:5], j.float(), mask), 1)[conf.view(-1) > 0]
        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        # print(scores)
        i = nms(boxes, scores, iou_thres)  # NMS
        i = i[:max_det]  # limit detections
        if merge and (1 < n < 3e3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if mps:
            output[xi] = output[xi].to(device)

    return output


class YOLOv5:
    label = ['Monster', 'Monster_ds', 'Monster_szt', 'card', 'equipment', 'go', 'hero', 'map', 'opendoor_d', 'opendoor_l', 'opendoor_r', 'opendoor_u', 'pet', 'Diamond']

    def __init__(self, model_path, image_queue, infer_queue, onFrame):
        self.path = model_path
        self.onFrame = onFrame
        self.image_queue = image_queue
        self.infer_queue = infer_queue
        self.runing = True
        self.stopFlag = True  # 默认不开启
        self.isFirst = True
        self.thread = threading.Thread(target=self.thread)  # 创建线程，并指定目标函数
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.thread.start()

    def start(self):
        self.stopFlag = False

    def stop(self):
        self.stopFlag = True

    def thread(self):
        DEBUG = False
        session = ort.InferenceSession(self.path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])  # 使用GPU推理，需要Cuda环境，否则运行报错
        # 获取模型输入输出信息
        input_name = session.get_inputs()[0].name
        output_names = [output.name for output in session.get_outputs()]
        currentProvider = session.get_providers()[0]
        if currentProvider == "CUDAExecutionProvider":
            print("当前使用的硬件加速器类型为:", session.get_providers()[0])
        else:
            print("GPU启用失败,请检查你的运行环境是否配置正确,此次运行加速器降级调整为:", session.get_providers()[0])
        while self.runing:
            if self.image_queue.empty():
                time.sleep(0.005)
                continue
            if self.stopFlag and not self.isFirst:
                img = self.image_queue.get()
                self.onFrame(img.copy(), None)
                continue
            if DEBUG:
                sAll = time.time()
                s = time.time()
            img0 = self.image_queue.get()
            img = img0
            img, radio, (dw, dh) = letterbox(img, [640, 640], stride=64, auto=False)
            top_pad = int(dh)
            img = img.transpose((2, 0, 1))[::-1]
            img = np.expand_dims(img, axis=0)
            img = np.ascontiguousarray(img)
            img = img.astype('float32')
            inputs = img / 255.0
            if len(img.shape) == 3:
                img = img[None]  # expand for batch dim
            if DEBUG:
                print(f'前期耗时{int((time.time() - s) * 1000)} ms')
                s = time.time()
            output = session.run(output_names, {input_name: inputs})
            if DEBUG:
                print(f'匹配耗时{int((time.time() - s) * 1000)} ms')
            if self.isFirst:
                self.isFirst = False
                print("onnxruntime 初始化完成")
                continue
            shape = (1, 25200, 19)
            output = np.resize(output[0], shape)
            output = self.from_numpy(output)
            output = NonMaximumSuppression(output)[0]
            output[:, 0] = output[:, 0]/640
            output[:, 1] = (output[:, 1] - top_pad)/(640-top_pad*2)
            output[:, 2] = output[:, 2]/640
            output[:, 3] = (output[:, 3] - top_pad)/(640-top_pad*2)
            if DEBUG:
                print(f'总计耗时{int((time.time() - sAll) * 1000)} ms')
            if self.runing:
                self.infer_queue.put([img0, output])
                actionManager.image = img0
                self.onFrame(img0, output)

    def quit(self):
        self.runing = False

    def from_numpy(self, x):
        """Converts a NumPy array to a torch tensor, maintaining device compatibility."""
        return torch.from_numpy(x) if isinstance(x, np.ndarray) else x
