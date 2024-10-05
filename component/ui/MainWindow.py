import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QStackedLayout, QSizePolicy, QCheckBox, QSlider, QFrame, QDesktopWidget
from component.ui.SizeHelper import toDp
from component.yolo.yolov5_onnx import YOLOv5
from component.action.game_action import GameAction
import component.utils.RuntimeData as R
from component.adb.scrcpy_adb import ScrcpyADB
from component.action.ActionManager import actionManager
from config import SHOW_MAP_POINT, SHOW_BUTTON, ALPHA, WINDOW_SCALE, WORKERS, VERSION
from component.ui.DrawLabel import DrawLabel
from component.utils.EventManager import eventManager
from PyQt5.QtGui import QFont


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.sizeChanging = False
        self.mousePressed = False
        self.mousePosition = None
        self.rightBarWidth = toDp(120)
        self.hSpace = toDp(3)
        self.initUI()
        eventManager.subscribe('FINISH_EVENT', self.onFinishEvent)

    def initUI(self):
        self.setWindowTitle(f'DNFM v{VERSION}')
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
        self.labelFrame = DrawLabel()
        self.labelFrame.setAlignment(Qt.AlignCenter)
        self.labelFrame.setMouseCallback(self.onFrameMouseEvent)
        self.labelFrame.drawMapPoint = True if SHOW_MAP_POINT else False
        self.labelFrame.drawButton = True if SHOW_BUTTON else False
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
        self.labelLoading = QLabel('正在查找设备，等待连接')
        self.labelLoading.setAlignment(Qt.AlignCenter)

        self.sbox = QStackedLayout()
        self.sbox.setStackingMode(QStackedLayout.StackAll)
        self.sbox.setAlignment(Qt.AlignCenter)
        self.sbox.addWidget(self.labelLoading)
        self.sbox.addWidget(self.labelFrame)

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
        # self.labelFrame.resize(1000, 450)
        # self.labelFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.labelLoading.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.checkBoxPoint.setChecked(self.labelFrame.drawMapPoint)
        self.checkBoxButtons.setChecked(self.labelFrame.drawButton)
        self.checkBoxMouse.setChecked(self.labelFrame.mouseContrl)
        self.slider.setOrientation(1)  # 设置为垂直方向
        self.slider.setRange(1, 100)
        self.slider.setValue(alpha)
        self.slider.setTickPosition(2)  # 设置刻度位置
        self.labelAlpha.setAlignment(Qt.AlignCenter)  # 设置文字居中显示
        
        fontText = QFont()
        fontText.setPointSize(toDp(8))  # 设置文字大小为16
        self.startBtn.setFont(fontText)
        self.resetBtn.setFont(fontText)
        self.screenshotBtn.setFont(fontText)
        self.checkBoxPoint.setFont(fontText)
        self.checkBoxButtons.setFont(fontText)
        self.checkBoxMouse.setFont(fontText)
        self.labelAlpha.setFont(fontText)
        self.labelLoading.setFont(fontText)
        
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
        w = R.FRAME_WIDTH+self.rightBarWidth+self.hSpace
        h = int(R.FRAME_WIDTH*R.RATE)
        w = int(w * WINDOW_SCALE)
        h = int(h * WINDOW_SCALE)
        x = screen.width() - w - 100
        y = screen.height() - h - 150
        self.setGeometry(x, y, w, h)

    def onFrameMouseEvent(self, eventType, x, y):
        if eventType == 2:
            self.client.touch_down(x, y, -1, False)
        elif eventType == 3:
            self.client.touch_up(x, y, -1, False)
        elif eventType == 5:
            self.client.touch_move(x, y, -1, False)

    def onFrame(self, frame, output):
        if not self.isVisible():
            return
        self.labelFrame.setFrame(frame, output, self.action.matchResultMap.copy(), self.action.ctrl.config)

    def __createHeroList(self):
        for heroNum in WORKERS:
            R.HEROS[heroNum] = False

    def onclick(self):
        if self.sender() is self.startBtn:
            if self.startBtn.text() == "start":
                self.startBtn.setText("stop")
                self.yolo.start()
                self.action.start()
                self.__createHeroList()
                actionManager.start()
            else:
                self.startBtn.setText("start")
                self.yolo.stop()
                self.action.stop()
                actionManager.stopAllAction()
        elif self.sender() is self.resetBtn:
            self.action.reset()
        elif self.sender() is self.screenshotBtn:
            self.client.screenshot()

    def onCheckBoxChanged(self, state):
        if self.sender() is self.checkBoxPoint:
            self.labelFrame.drawMapPoint = True if state == 2 else False
        elif self.sender() is self.checkBoxButtons:
            self.labelFrame.drawButton = True if state == 2 else False
        elif self.sender() is self.checkBoxMouse:
            self.labelFrame.mouseContrl = True if state == 2 else False

    def onSliderChanged(self):
        value = self.slider.value()
        self.labelAlpha.setText(f'透明度:{value}%')
        self.setWindowOpacity(value/100)

    def setComponents(self, client, yolo, action):
        self.client: ScrcpyADB = client
        self.yolo: YOLOv5 = yolo
        self.action: GameAction = action

    def onFinishEvent(self):
        self.startBtn.click()

    def closeEvent(self, event):
        print("退出")
        self.yolo.quit()
        self.client.stop()
        self.action.quit()

    def onConnect(self):
        self.labelFrame.show()
        self.labelLoading.hide()

    def onDisConnect(self):
        self.labelFrame.hide()
        self.labelLoading.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    t = MainWindow()
    t.show()
    app.exec_()
