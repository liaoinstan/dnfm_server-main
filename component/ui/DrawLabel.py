from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QPainter,  QFont, QColor,  QTransform, QPen, QFontMetrics
from PyQt5.QtWidgets import QLabel
import cv2
import time
from component.yolo.yolov5_onnx import YOLOv5
from component.utils.BWJRoomHelperV2 import roomHelper
from component.utils.ButtonHelper import buttonHelper
import component.utils.RuntimeData as R
from component.ui.SizeHelper import toDp
from config import CENTER_POINT, OFFSET_ROOM
from component.utils.BWJRoomHelperV2 import roomHelper


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
        self.frameCount = 0
        self.frameTime = 0
        self.fps = 0

        self.output = None

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
        self.output = output

        self.frameCount += 1
        if self.frameCount >= 120:
            self.frameCount = 0
            self.frameTime = 0
        if self.frameTime == 0:
            self.frameTime = time.time()
        else:
            timeGap = int((time.time() - self.frameTime) * 1000)
            self.fps = int(self.frameCount/timeGap*1000)
            # print("fps",fps,self.frameCount)
        if frame is not None:
            # 绘制小地图锚点
            # if self.drawMapPoint:
            # roomHelper.drawMapPoint(frame)
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

    def __box2PixXYWH(self, pixRect: QRect, box):
        det_x1, det_y1, det_x2, det_y2, conf, label = box
        x1 = int(det_x1*pixRect.width() + pixRect.x())
        y1 = int(det_y1*pixRect.height() + pixRect.y())
        x2 = int(det_x2*pixRect.width() + pixRect.x())
        y2 = int(det_y2*pixRect.height() + + pixRect.y())
        return (x1, y1, x2-x1, y2-y1)

    def paintEvent(self, event):
        super().paintEvent(event)
        pixmap = self.pixmap()
        if pixmap is None:
            return
        if self.mousePointTimeOut != 0 and int((time.time() - self.mousePointTimeOut) * 1000) > 2000:
            self.mousePosition = None

        # 计算画布坐标
        labelWidth = self.size().width()
        labelHeight = self.size().height()
        pixWidth = self.pixmap().size().width()
        pixHeight = self.pixmap().size().height()
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
        # 计算缩放值
        perWidth = 1000
        scale = pixWidth/perWidth
        # 缩放画布坐标
        rectScale = QRect(rect.x()/scale, rect.y()/scale, rect.width()/scale, rect.height()/scale)

        # 绘制
        painter = QPainter(self)
        painter.setPen(QColor('green'))

        # 绘制dubug区域
        if self.debug:
            painter.setBrush(QColor(0, 0, 255, 128))
            painter.drawRect(rectScale)

        if self.output is not None:
            titleHPadding = toDp(5)
            lineWidth = toDp(3)
            font = QFont('Arial', 8)
            font.setWeight(QFont.Bold)
            painter.setFont(font)
            for boxs in self.output:
                x, y, w, h = self.__box2PixXYWH(rect, boxs)
                conf = "{:.2f}".format(boxs[4])
                label = boxs[5]
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
                elif label == 4:
                    # equipment
                    color = (245, 143, 0)
                else:
                    color = (0, 255, 0)
                color = QColor(color[0], color[1], color[2])
                pen = QPen(color)
                pen.setWidth(lineWidth)
                painter.setPen(pen)
                painter.setBrush(Qt.transparent)
                painter.drawRect(x, y, w, h)

                labelName = YOLOv5.label[int(label)]
                text = f'{labelName} {conf}'

                # 计算文字高宽
                font_metrics = QFontMetrics(painter.font())
                text_width = font_metrics.horizontalAdvance(text)
                text_height = font_metrics.height()

                if label == 13:
                    continue
                # 绘制标题背景
                rectTitle = QRect(x, y-text_height, text_width+titleHPadding*2, text_height)
                painter.setBrush(color)
                painter.drawRect(rectTitle)

                # 绘制标题文字
                pen.setColor(Qt.white)
                painter.setPen(pen)
                painter.drawText(rectTitle, Qt.AlignCenter, text)

        if self.drawMapPoint:
            self.drawMapPoints(painter, rect)

        # 文本缩放绘制
        transform = QTransform()
        transform.scale(scale, scale)
        painter.setTransform(transform)

        if self.mousePosition is not None:
            # 绘制坐标
            font = QFont('Arial', 10)
            painter.setFont(font)
            painter.setPen(QColor('green'))
            self.text = f'{self.mousePosition[0].x(),self.mousePosition[0].y()}-窗口坐标\n{self.mousePosition[1].x(),self.mousePosition[1].y()}-设备坐标'
            painter.drawText(rectScale, Qt.AlignRight | Qt.AlignBottom, self.text)
        # 绘制FPS
        painter.setPen(QColor('red'))
        font = QFont('Arial', 6)
        painter.setFont(font)
        painter.drawText(rectScale, Qt.AlignLeft | Qt.AlignTop, f'FPS:{self.fps}')

    def drawMapPoints(self, painter: QPainter, pixRect: QRect):
        color = QColor('red')
        painter.setPen(color)
        painter.setBrush(color)

        def valueframe2Label(value):
            rateLabelFrame = self.pixmap().width()/R.FRAME_WIDTH
            return value * rateLabelFrame

        def framePiont2labelPoint(x, y, pixRect: QRect):
            x = valueframe2Label(x) + pixRect.x()
            y = valueframe2Label(y) + pixRect.y()
            return x, y

        def drawCircle(cx, cy, r):
            painter.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)
        r = int(R.SCALE * valueframe2Label(5))
        x, y = framePiont2labelPoint(*roomHelper.center, pixRect)
        offR = valueframe2Label(roomHelper.offsetRoom)
        offA = valueframe2Label(roomHelper.offsetArrow)

        drawCircle(x+offR, y+offR, r)
        drawCircle(x+offR, y-offR, r)
        drawCircle(x-offR, y+offR, r)
        drawCircle(x-offR, y-offR, r)
        drawCircle(x, y+offR, r)
        drawCircle(x, y-offR, r)
        drawCircle(x+offR, y, r)
        drawCircle(x-offR, y, r)
        drawCircle(x, y, r)
        drawCircle(x, y+offA, r)
        drawCircle(x, y-offA, r)
        drawCircle(x+offA, y, r)
        drawCircle(x-offA, y, r)

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
