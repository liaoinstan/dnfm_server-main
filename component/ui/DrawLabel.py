from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QPainter,  QFont, QColor,  QTransform
from PyQt5.QtWidgets import QLabel
import cv2
import time
from component.utils.yolov5_onnx import YOLOv5
from component.utils.BWJRoomHelperV2 import roomHelper
from component.utils.ButtonHelper import buttonHelper
import component.utils.RuntimeData as R


class DrawLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.mousePressEvent = self.onMouseEvent
        self.mouseMoveEvent = self.onMouseEvent
        self.mouseReleaseEvent = self.onMouseEvent
        self.drawMapPoint = False
        self.drawButton = False
        self.mouseContrl = True
        self.mousePointTimeOut = 0
        self.mousePosition = None
        self.mousePressed = False
        self.debug = False
        self.lastPixmap = None

    def setMouseCallback(self, callbackFrameMouseEvent):
        self.callbackFrameMouseEvent = callbackFrameMouseEvent

    def __resizePixmap(self, pix: QPixmap):
        rate = R.RATE
        labelRate = self.size().height()/self.size().width()
        if labelRate < rate:
            height = self.size().height()
            width = int(height / rate)
        else:
            width = self.size().width()
            height = int(width * rate)
        return pix.scaled(width, height, Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        pix = self.lastPixmap
        if pix is not None:
            pix = self.__resizePixmap(pix)
            self.setPixmap(pix)

    def setFrame(self, frame, output, matchDict=None, buttons=None):
        if frame is not None:
            if output is not None:
                for boxs in output:
                    det_x1, det_y1, det_x2, det_y2, conf, label = boxs
                    x1 = int(det_x1*frame.shape[1])
                    y1 = int(det_y1*frame.shape[0])
                    x2 = int(det_x2*frame.shape[1])
                    y2 = int(det_y2*frame.shape[0])
                    if label <= 2:
                        # monster
                        color = (255, 55, 0)
                    elif label == 6:
                        # hero
                        color = (0, 0, 255)
                    elif label >= 8 and label <= 11:
                        # door
                        color = (14, 209, 0)
                    elif label == 5:
                        # go
                        color = (0, 213, 255)
                    else:
                        color = (0, 255, 0)
                    color = (color[2], color[1], color[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, "{:.2f}".format(conf), (int(x1), int(
                        y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    cv2.putText(frame, YOLOv5.label[int(label)], (int(x1), int(
                        y1-30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            # 绘制小地图锚点
            if self.drawMapPoint:
                roomHelper.drawMapPoint(frame)
            # 绘制小地图
            roomHelper.drawMiniMap(frame)
            # 绘制技能按钮
            if self.drawButton:
                buttonHelper.drawButtons(frame, buttons)
            # 绘制模版匹配区域
            if len(matchDict) > 0:
                for matchDataList in matchDict.values():
                    for matchData in matchDataList:
                        cx, cy, w, h = matchData[0], matchData[1], matchData[2], matchData[3]
                        top_left = (cx - w//2, cy-h//2)
                        bottom_right = (top_left[0] + w, top_left[1] + h)
                        cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255), 2)

            image = QImage(
                frame,
                frame.shape[1],
                frame.shape[0],
                frame.shape[1] * 3,
                QImage.Format_BGR888,
            )
            pix = QPixmap(image)
            pix = self.__resizePixmap(pix)
            self.setPixmap(pix)
            self.lastPixmap = pix

    def paintEvent(self, event):
        super().paintEvent(event)
        pixmap = self.pixmap()
        if pixmap is None:
            return
        if self.mousePointTimeOut != 0 and int((time.time() - self.mousePointTimeOut) * 1000) > 2000:
            self.mousePosition = None
        if self.mousePosition is None:
            return
        painter = QPainter(self)
        self.text = f'{self.mousePosition[0].x(),self.mousePosition[0].y()}-窗口坐标\n{self.mousePosition[1].x(),self.mousePosition[1].y()}-设备坐标'
        # 计算缩放值
        textSize = 10
        perWidth = 1000
        labelWidth = self.size().width()
        labelHeight = self.size().height()
        pixWidth = self.pixmap().size().width()
        pixHeight = self.pixmap().size().height()
        scale = pixWidth/perWidth

        # 计算画布坐标
        labelRate = labelHeight/labelWidth
        pixRate = pixHeight/pixWidth
        if labelRate < pixRate:
            x = int((labelWidth-pixWidth)/2)
            y = 0
        else:
            x = 0
            y = int((labelHeight-pixHeight)/2)
        # 画布坐标
        rect = QRect(x, y, pixWidth, pixHeight)
        # 缩放画布坐标
        rectScale = QRect(rect.x()/scale, rect.y()/scale, rect.width()/scale, rect.height()/scale)

        transform = QTransform()
        transform.scale(scale, scale)
        font = QFont('Arial', textSize)
        painter.setTransform(transform)
        painter.setFont(font)
        painter.setPen(QColor('green'))

        # 绘制dubug区域
        if self.debug:
            painter.setBrush(QColor(0, 0, 255, 128))
            painter.drawRect(rectScale)
        # 绘制坐标
        painter.drawText(rectScale, Qt.AlignRight | Qt.AlignBottom, self.text)

    def onMouseEvent(self, evt: QMouseEvent):
        if not self.mouseContrl:
            return
        if self.pixmap() is None:
            return
        labelWidth = self.size().width()
        labelHeight = self.size().height()
        pixWidth = self.pixmap().size().width()
        pixHeight = self.pixmap().size().height()
        labelRate = labelHeight/labelWidth
        pixRate = pixHeight/pixWidth
        # 窗口坐标转画布坐标
        if labelRate < pixRate:
            x = evt.pos().x() - int((labelWidth-pixWidth)/2)
            y = evt.pos().y()
        else:
            x = evt.pos().x()
            y = evt.pos().y() - int((labelHeight-pixHeight)/2)
        # 画布坐标转手机坐标
        rate = pixWidth/R.FRAME_WIDTH
        fx = int(x/rate)
        fy = int(y/rate)
        if evt.type() == 2:
            # 按下
            self.mousePressed = True
            self.callbackFrameMouseEvent(evt.type(), fx, fy)
        elif evt.type() == 3:
            # 抬起
            self.mousePressed = False
            self.callbackFrameMouseEvent(evt.type(), fx, fy)
        elif evt.type() == 5:
            # 移动
            if self.mousePressed:
                self.callbackFrameMouseEvent(evt.type(), fx, fy)

        if x >= 0 and x <= pixWidth and y >= 0 and y <= pixHeight:
            sx = int(fx/R.SCALE)
            sy = int(fy/R.SCALE)
            self.mousePosition = (QPoint(fx, fy), QPoint(sx, sy))
            self.mousePointTimeOut = time.time()
        self.update()
