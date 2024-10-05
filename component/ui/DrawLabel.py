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
from config import CENTER_POINT, OFFSET_ROOM, JITTER, WORKERS
from component.utils.BWJRoomHelperV2 import roomHelper
from hero.hero import Hero
from collections import deque

'''
自定义控件
该控件是主界面的UI画布,负责封装绘制和触控功能
1.绘制游戏画面
    1.1:游戏画面随窗口缩放自适应
2.鼠标控制逻辑
    2.1:鼠标坐标转手机坐标
3.绘制小地图和锚点
4.绘制技能按钮
5.绘制对象矩阵
6.绘制模版匹配区域
7.绘制屏幕坐标
8.计算FPS
'''


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
        self.pixRect = None
        self.rateLabelFrame: float = 0
        self.fps = 0
        self.output = None
        self.matchDict = None
        self.buttons = None

    def setMouseCallback(self, callbackFrameMouseEvent):
        self.callbackFrameMouseEvent = callbackFrameMouseEvent

    def resizeEvent(self, event):
        pix = self.lastPixmap
        if pix is None:
            return
        pix = self.__resizePixmap(pix)
        self.setPixmap(pix)
        self.__calcuPixRect()

    def setFrame(self, frame, output, matchDict=None, buttons=None):
        self.output = output
        self.matchDict = matchDict
        self.buttons = buttons
        self.frameCount += 1
        if self.frameCount >= 120:
            self.frameCount = 0
            self.frameTime = 0
        # 计算fps
        if self.frameTime == 0:
            self.frameTime = time.time()
        else:
            timeGap = int((time.time() - self.frameTime) * 1000)
            self.fps = int(self.frameCount/timeGap*1000)
        # 画布绘制
        if frame is not None:
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
        if self.pixRect is None:
            self.__calcuPixRect()
        if self.mousePointTimeOut != 0 and int((time.time() - self.mousePointTimeOut) * 1000) > 2000:
            self.mousePosition = None

        # 初始化绘制
        painter = QPainter(self)
        painter.setPen(QColor('green'))
        # 绘制dubug区域
        if self.debug:
            painter.setBrush(QColor(0, 0, 255, 128))
            painter.drawRect(self.pixRect)
        # 绘制对象标识
        self.__drawObjects(painter)
        # 绘制地图锚点
        if self.drawMapPoint:
            self.__drawMapPoints(painter)
        # 绘制小地图
        self.__drawMiniMap(painter)
        # 绘制模版匹配区域
        self.__drawMatchRect(painter)
        if self.drawButton:
            self.__drawButtons(painter, self.buttons)

        # 计算缩放值
        perWidth = 1000
        scale = self.pixRect.width()/perWidth
        rectScale = QRect(self.pixRect.x()/scale, self.pixRect.y()/scale, self.pixRect.width()/scale, self.pixRect.height()/scale)
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

    ################################## 私有方法########################################

    def __calcuPixRect(self):
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
        self.pixRect = QRect(x, y, pixWidth, pixHeight)
        self.rateLabelFrame = self.pixmap().width()/R.FRAME_WIDTH

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

    def __valueframe2Label(self, value):
        return value * self.rateLabelFrame

    def __framePiont2labelPoint(self, x, y):
        x = self.__valueframe2Label(x) + self.pixRect.x()
        y = self.__valueframe2Label(y) + self.pixRect.y()
        return x, y

    def __framRect2labelRect(self, x, y, w, h):
        x = self.__valueframe2Label(x) + self.pixRect.x()
        y = self.__valueframe2Label(y) + self.pixRect.y()
        w = self.__valueframe2Label(w)
        h = self.__valueframe2Label(h)
        return x, y, w, h

    def __box2PixXYWH(self, box):
        det_x1, det_y1, det_x2, det_y2, conf, label = box
        x1 = int(det_x1*self.pixRect.width() + self.pixRect.x())
        y1 = int(det_y1*self.pixRect.height() + self.pixRect.y())
        x2 = int(det_x2*self.pixRect.width() + self.pixRect.x())
        y2 = int(det_y2*self.pixRect.height() + + self.pixRect.y())
        return (x1, y1, x2-x1, y2-y1)

    def __calcuText(self, painter: QPainter, text: str):
        lines = text.split('\n')
        font_metrics = QFontMetrics(painter.font())
        textWidth = 0
        textHeight = 0
        for line in lines:
            lineWidth = font_metrics.horizontalAdvance(line)
            lineHeight = font_metrics.height()
            if lineWidth > textWidth:
                textWidth = lineWidth
            textHeight += lineHeight
        return textWidth, textHeight

    def _getKeyByValue(self, d, value):
        for key, val in d.items():
            if val == value:
                return key
        return None

    def __drawObjects(self, painter: QPainter):
        if self.output is None:
            return
        lineWidth = toDp(3)
        titleHPadding = toDp(5)
        font = QFont('Arial', 8)
        font.setWeight(QFont.Bold)
        painter.setFont(font)
        for boxs in self.output:
            x, y, w, h = self.__box2PixXYWH(boxs)
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
            # 绘制对象区域
            painter.drawRect(x, y, w, h)
            if label == 13:
                continue
            # 计算文字高宽
            labelName = YOLOv5.label[int(label)]
            text = f'{labelName} {conf}'
            font_metrics = QFontMetrics(painter.font())
            text_width = font_metrics.horizontalAdvance(text)
            text_height = font_metrics.height()
            # 绘制标题背景
            rectTitle = QRect(x, y-text_height, text_width+titleHPadding*2, text_height)
            color.setAlpha(100)
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawRect(rectTitle)
            # 绘制标题文字
            pen.setColor(Qt.white)
            painter.setPen(pen)
            painter.drawText(rectTitle, Qt.AlignCenter, text)

    def __drawMatchRect(self, painter: QPainter):
        lineWidth = toDp(3)
        pen = QPen(QColor('red'))
        pen.setWidth(lineWidth)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        if len(self.matchDict) > 0:
            for matchDataList in self.matchDict.values():
                for matchData in matchDataList:
                    cx, cy, w, h = matchData[0], matchData[1], matchData[2], matchData[3]
                    cx, cy = self.__framePiont2labelPoint(cx, cy)
                    w = self.__valueframe2Label(w)
                    h = self.__valueframe2Label(h)
                    rectMatch = QRect(cx - w//2, cy-h//2, w, h)
                    painter.drawRect(rectMatch)

    def __drawMapPoints(self, painter: QPainter):
        def drawCircle(cx, cy, r):
            painter.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)

        color = QColor('red')
        painter.setPen(color)
        painter.setBrush(color)
        r = int(R.SCALE * self.__valueframe2Label(5))
        x, y = self.__framePiont2labelPoint(*roomHelper.center)
        offR = self.__valueframe2Label(roomHelper.offsetRoom)
        offA = self.__valueframe2Label(roomHelper.offsetArrow)

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

    def __drawButtons(self, painter: QPainter, skillData):
        def drawCircle(cx, cy, r):
            painter.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)
        skills = None
        if R.CURRENT_HERO is not None:
            hero = Hero.getInstance(WORKERS[R.CURRENT_HERO])
            if hero is not None:
                skills = hero.dict
        lineWidth = toDp(3)
        color = QColor('red')
        pen = QPen(color)
        pen.setWidth(lineWidth)
        font = QFont('Arial', 8)
        font.setWeight(QFont.Bold)
        painter.setFont(font)
        scale = R.SCALE
        jitter = int(JITTER*scale)
        for key, value in skillData.items():
            if key == "joystick":
                radius = int(value["radius"]*scale)
                value = value["center"]
                centerArea = (int(value[0]*scale), int(value[1]*scale))
                centerArea = self.__framePiont2labelPoint(*centerArea)
                radius = self.__valueframe2Label(radius)
                painter.setBrush(Qt.transparent)
                drawCircle(*centerArea, radius)
            if isinstance(value, str):
                continue
            if skills is not None and key in skills.values():
                key = key+'\n' + self._getKeyByValue(skills, key)
            # 绘制按钮区域
            center = (int(value[0]*scale), int(value[1]*scale))
            textWidth, textHeight = self.__calcuText(painter, key)
            textRect = (center[0]-textWidth//2, center[1]-textHeight-toDp(10), textWidth, textHeight)
            textRect = QRect(*self.__framRect2labelRect(*textRect))
            center = self.__framePiont2labelPoint(*center)
            painter.setPen(pen)
            painter.setBrush(color)
            drawCircle(*center, jitter)
            # 绘制按钮文本背景
            bkColor = QColor(0, 0, 255, 100)
            painter.setPen(bkColor)
            painter.setBrush(bkColor)
            painter.drawRect(textRect)
            # 绘制按钮文本
            painter.setPen(QColor('white'))
            painter.drawText(textRect, Qt.AlignCenter, key)

    # 绘制一张可视化小地图
    def __drawMiniMap(self, painter: QPainter):
        # 根据屏幕大小计算绘制参数
        lines = (3, 6, 3)
        width = self.pixRect.width()
        height = self.pixRect.height()
        w = int(width*0.015)
        margin = int(w * 0.3)
        wMax = w * 6 + margin * 5
        hMax = w * 3 + margin * 2
        startX = (width - wMax) // 2
        startY = height // 40
        endX = startX + wMax
        endY = startY + hMax
        lineWidth = toDp(3)
        # 创建一张有alpha通道的空画布，并绘制小地图
        cleanedRoom = roomHelper.cleanedRoom
        map = {0: 9, 1: -2, 2: 10, 3: 0, 4: 5, 5: 4, 6: 6, 7: 7, 8: 8, 9: 1, 10: 2, 11: 3}
        n = 0
        for i in range(0, len(lines)):
            y = i*(w+margin) + self.pixRect.y() + height//18
            for j in range(0, lines[i]):
                x = j*(w+margin) + self.pixRect.x() + width//2 - wMax//2
                if map[n] in cleanedRoom:
                    color = QColor(155, 155, 155, 180)
                elif n == 4:
                    color = QColor(186, 99, 3, 180)
                elif n == 8:
                    color = QColor(158, 0, 0, 180)
                else:
                    color = QColor(33, 33, 33, 180)
                painter.setPen(color)
                painter.setBrush(color)
                painter.drawRect(QRect(x, y, w, w))
                if len(cleanedRoom) > 0:
                    roomNow = deque(cleanedRoom.keys(), maxlen=1)[0]
                    nNow = next(key for key, value in map.items() if value == roomNow)
                    if n == nNow:
                        pen = QPen(QColor(0, 255, 0, 128))
                        pen.setWidth(lineWidth)
                        painter.setPen(pen)
                        painter.setBrush(Qt.transparent)
                        painter.drawRect(QRect(x-lineWidth, y-lineWidth, w+lineWidth*2, w+lineWidth*2))
                n += 1
