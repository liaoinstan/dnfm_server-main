import sys

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QStackedLayout, QSizePolicy, QCheckBox, QSlider, QFrame, QDesktopWidget
from ui.SizeHelper import toDp
import cv2
from utils.yolov5_onnx import YOLOv5
from utils.BWJRoomHelperV2 import roomHelper
from utils.ButtonHelper import buttonHelper
from game_action import GameAction
import utils.RuntimeData as R
from scrcpy_adb import ScrcpyADB
from action.ActionManager import actionManager
from config import SHOW_MAP_POINT, SHOW_BUTTON, ALPHA, WINDOW_SCALE, WORKERS

version = "1.1.0A"


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.onSizeChanged)
        self.sizeChanging = False
        self.lastPixmap = None
        self.drawMapPoint = True if SHOW_MAP_POINT else False
        self.drawButton = True if SHOW_BUTTON else False
        self.mouseContrl = True
        self.mouseTrack = []
        self.rightBarWidth = toDp(120)
        self.hSpace = toDp(3)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'DNFM v{version}')
        self.setGeometry(100, 100, 100, 100)
        self.setWindowOpacity(0.75)
        self.setMinimumSize(100, 100)
        alpha = int(ALPHA * 100)
        if alpha <= 0:
            alpha = 1
        elif alpha > 100:
            alpha = 100
        vline = QFrame()
        vline.setFrameShape(QFrame.VLine)
        vline.setFrameShadow(QFrame.Sunken)
        spacer = QWidget()
        spacer.setFixedSize(3, 3)
        self.labelFrame = QLabel(self)
        self.labelFrame.setAlignment(Qt.AlignCenter)
        self.labelFrame.mousePressEvent = self.onMouseEvent
        self.labelFrame.mouseMoveEvent = self.onMouseEvent
        self.labelFrame.mouseReleaseEvent = self.onMouseEvent
        self.startBtn = QPushButton("start")
        self.startBtn.clicked.connect(self.onclick)
        self.resetBtn = QPushButton("reset")
        self.resetBtn.clicked.connect(self.onclick)
        self.screenshotBtn = QPushButton("screenshot")
        self.screenshotBtn.clicked.connect(self.onclick)
        self.checkBoxPoint = QCheckBox('地图锚点', self)
        self.checkBoxPoint.stateChanged.connect(self.onCheckBoxChanged)
        self.checkBoxButtons = QCheckBox('技能按钮', self)
        self.checkBoxButtons.stateChanged.connect(self.onCheckBoxChanged)
        self.checkBoxMouse = QCheckBox('鼠标操作', self)
        self.checkBoxMouse.stateChanged.connect(self.onCheckBoxChanged)
        self.slider = QSlider()
        self.slider.valueChanged.connect(self.onSliderChanged)
        self.labelAlpha = QLabel('')
        labelLoading = QLabel('正在查找设备，等待连接')
        labelLoading.setAlignment(Qt.AlignCenter)

        self.sbox = QStackedLayout()
        self.sbox.setAlignment(Qt.AlignCenter)
        self.sbox.addWidget(self.labelFrame)
        self.sbox.addWidget(labelLoading)
        self.sbox.setCurrentIndex(1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.startBtn)
        vbox.addWidget(self.resetBtn)
        vbox.addWidget(self.screenshotBtn)
        vbox.addWidget(self.checkBoxPoint)
        vbox.addWidget(self.checkBoxButtons)
        vbox.addWidget(self.checkBoxMouse)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.labelAlpha)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(self.sbox)
        hbox.addWidget(vline)
        hbox.addWidget(spacer)
        hbox.addLayout(vbox)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.setContentsMargins(0, 0, 0, 0)
        # self.label.setScaledContents(True)
        self.labelFrame.resize(1000, 450)
        self.labelFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        labelLoading.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.checkBoxPoint.setChecked(self.drawMapPoint)
        self.checkBoxButtons.setChecked(self.drawButton)
        self.checkBoxMouse.setChecked(self.mouseContrl)
        self.slider.setOrientation(1)  # 设置为垂直方向
        self.slider.setRange(1, 100)
        self.slider.setValue(alpha)
        self.slider.setTickPosition(2)  # 设置刻度位置
        self.labelAlpha.setAlignment(Qt.AlignCenter)  # 设置文字居中显示

        btnWidth = self.rightBarWidth
        btnHeight = toDp(30)
        self.startBtn.setFixedSize(btnWidth, btnHeight)
        self.resetBtn.setFixedSize(btnWidth, btnHeight)
        self.screenshotBtn.setFixedSize(btnWidth, btnHeight)
        self.checkBoxPoint.setFixedSize(btnWidth, btnHeight)
        self.checkBoxButtons.setFixedSize(btnWidth, btnHeight)
        self.checkBoxMouse.setFixedSize(btnWidth, btnHeight)
        self.slider.setFixedSize(btnWidth, btnHeight)
        self.labelAlpha.setFixedSize(btnWidth, btnHeight)

        self.setLayout(hbox)

    def resizeToDefault(self):
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        w = R.FRAME_WIDTH+self.rightBarWidth+self.hSpace
        h = int(R.FRAME_WIDTH*R.RATE)
        w = int(w * WINDOW_SCALE)
        h = int(h * WINDOW_SCALE)
        x = screen.width() - w - 100
        y = screen.height() - h - 150
        self.setGeometry(x, y, w, h)

    def onFrame(self, frame, output):
        if not self.isVisible():
            return
        if self.timer.isActive():
            return
        if frame is not None:

            for boxs in output:
                det_x1, det_y1, det_x2, det_y2, conf, label = boxs
                x1 = int(det_x1*frame.shape[1])
                y1 = int(det_y1*frame.shape[0])
                x2 = int(det_x2*frame.shape[1])
                y2 = int(det_y2*frame.shape[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "{:.2f}".format(conf), (int(x1), int(
                    y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, YOLOv5.label[int(label)], (int(x1), int(
                    y1-30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            if self.drawMapPoint:
                roomHelper.drawMapPoint(frame)
            roomHelper.drawMiniMap(frame)
            if self.drawButton:
                buttonHelper.drawButtons(frame, self.action.ctrl.config)

            matchDict = self.action.matchResultMap.copy()
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
            self.labelFrame.setPixmap(pix)
            self.lastPixmap = pix

    def __resizePixmap(self, pix: QPixmap):
        rate = R.RATE
        labelRate = self.labelFrame.size().height()/self.labelFrame.size().width()
        if labelRate < rate:
            height = self.labelFrame.size().height()
            width = int(height / rate)
        else:
            width = self.labelFrame.size().width()
            height = int(width * rate)
        return pix.scaled(width, height, Qt.KeepAspectRatio)

    def __createHeroList(self):
        # if self.heroStr is not None and len(self.heroStr) > 0:
            # R.HEROS = {int(x): False for x in self.heroStr.split(",")}
        for heroNum in WORKERS:
            R.HEROS[heroNum] = False

    def onclick(self):
        if self.sender() is self.startBtn:
            if self.startBtn.text() == "start":
                self.startBtn.setText("stop")
                self.action.stop_event = False
                self.__createHeroList()
                actionManager.start()
            else:
                self.startBtn.setText("start")
                self.action.stop_event = True
                actionManager.stopAllAction()
        elif self.sender() is self.resetBtn:
            self.action.reset()
        elif self.sender() is self.screenshotBtn:
            self.client.screenshot()

    def onCheckBoxChanged(self, state):
        if self.sender() is self.checkBoxPoint:
            self.drawMapPoint = True if state == 2 else False
        elif self.sender() is self.checkBoxButtons:
            self.drawButton = True if state == 2 else False
        elif self.sender() is self.checkBoxMouse:
            self.mouseContrl = True if state == 2 else False

    def onSliderChanged(self):
        value = self.slider.value()
        self.labelAlpha.setText(f'透明度:{value}%')
        self.setWindowOpacity(value/100)

    def onMouseEvent(self, evt: QMouseEvent):
        if not self.mouseContrl:
            return
        if self.labelFrame is None or self.labelFrame.pixmap() is None:
            return
        labelWidth = self.labelFrame.size().width()
        labelHeight = self.labelFrame.size().height()
        pixWidth = self.labelFrame.pixmap().size().width()
        pixHeight = self.labelFrame.pixmap().size().height()
        labelRate = labelHeight/labelWidth
        pixRate = pixHeight/pixWidth
        # print("label:", labelWidth, labelHeight, "pix:", pixWidth, pixHeight)
        # 窗口坐标转画布坐标
        if labelRate < pixRate:
            x = evt.pos().x() - int((labelWidth-pixWidth)/2)
            y = evt.pos().y()
        else:
            x = evt.pos().x()
            y = evt.pos().y() - int((labelHeight-pixHeight)/2)
        # 画布坐标转手机坐标
        rate = pixWidth/R.FRAME_WIDTH
        x = int(x/rate)
        y = int(y/rate)
        if evt.type() == 2:
            # 按下
            self.mouseTrack.append((x, y))
            self.client.touch_down(x, y, -1, False)
        elif evt.type() == 3:
            # 抬起
            self.mouseTrack.clear()
            self.client.touch_up(x, y, -1, False)
        elif evt.type() == 5:
            # 移动
            self.mouseTrack.append((x, y))
            self.client.touch_move(x, y, -1, False)
        # self.update()

    def setComponents(self, client, yolo, action):
        self.client: ScrcpyADB = client
        self.yolo = yolo
        self.action: GameAction = action

    def paintEvent(self, event):
        pass
        # super().paintEvent(event)
        # painter = QPainter(self)
        # painter.setRenderHint(painter.Antialiasing)
        # pen = QPen(Qt.red)
        # pen.setWidth(2)
        # painter.setPen(pen)
        # painter.setBrush(Qt.red)
        # lastPoint = None
        # painter.drawLine(QPoint(50,50),QPoint(850,850))
        # for point in self.mouseTrack:
        #     if lastPoint:
        #         painter.drawLine(QPoint(lastPoint[0], lastPoint[1]), QPoint(point[0], point[1]))
        #     lastPoint = point

    def resizeEvent(self, event):
        if event.oldSize().width() != -1:
            self.timer.start(500)

        pix = self.lastPixmap
        if pix is not None:
            pix = self.__resizePixmap(pix)
            self.labelFrame.setPixmap(pix)

    def onSizeChanged(self):
        self.timer.stop()

    def closeEvent(self, event):
        self.yolo.stop()
        self.client.stop()
        self.action.quit()

    def onConnect(self):
        self.sbox.setCurrentIndex(0)

    def onDisConnect(self):
        self.sbox.setCurrentIndex(1)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    t = MainWindow()
    t.show()
    app.exec_()
