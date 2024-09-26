from config import LOG_MATCH, TUNING_MATCH
import cv2
import numpy as np

TEMPLATE_DEVICE_WIDTH = 1440
TEMPLATE_DEVICE_HEIGHT = 3200


def __resize_template(large_image, template_image):
    rateTemplate = TEMPLATE_DEVICE_WIDTH/TEMPLATE_DEVICE_HEIGHT
    imageHeight, imageWidth = large_image.shape[:2]
    deviceRate = imageHeight/imageWidth
    if rateTemplate < deviceRate:
        caculRate = imageHeight/TEMPLATE_DEVICE_WIDTH
    else:
        caculRate = imageWidth/TEMPLATE_DEVICE_HEIGHT
    caculRate = caculRate*TUNING_MATCH
    return cv2.resize(template_image, (int(template_image.shape[1]*caculRate), int(template_image.shape[0]*caculRate)))

def match_template(large_image, template_image_path, threshold=0.7):
    # 读取大图和模板图
    template_image = cv2.imread(f'template/{template_image_path}')
    if large_image is None or template_image is None:
        raise ValueError("无法读取图片，请检查图片路径是否正确:", f'template/{template_image_path}')

    # 根据预设图片和设备分辨率对模版进行缩放
    template_image = __resize_template(large_image, template_image)

    # 使用模板匹配方法查找匹配位置
    result = cv2.matchTemplate(large_image, template_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if LOG_MATCH:
        print("匹配精度：", max_val)

    w, h = template_image.shape[1], template_image.shape[0]

    # 判断是否匹配成功
    if max_val >= threshold:
        # 计算匹配区域的中心点坐标
        top_left = max_loc
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        return center_x, center_y, w, h
    else:
        return None


def match_templates(large_image, template_image_path, threshold=0.7):
    # 读取大图和模板图
    template_image = cv2.imread(f'template/{template_image_path}')
    if large_image is None or template_image is None:
        raise ValueError("无法读取图片，请检查图片路径是否正确:", f'template/{template_image_path}')

    # 根据预设图片和设备分辨率对模版进行缩放
    template_image = __resize_template(large_image, template_image)

    # 使用模板匹配方法查找匹配位置
    result = cv2.matchTemplate(large_image, template_image, cv2.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)
    # 获取匹配结果的坐标和匹配值
    points = list(zip(*loc[::-1]))
    # 使用轮廓检测和边界框合并
    w, h = template_image.shape[1], template_image.shape[0]
    rectangles = []
    for point in points:
        x, y = point
        rectangles.append([x, y, w, h])
    rectangles, weights = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.2)
    # xywh转cxcywh
    results = []
    for rect in rectangles:
        x, y, w, h = rect[0], rect[1], rect[2], rect[3]
        results.append((x+w//2, y+h//2, w, h))

    if len(results) > 0:
        return results
    else:
        None
