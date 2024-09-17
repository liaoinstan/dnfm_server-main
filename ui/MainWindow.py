import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QSizePolicy, QCheckBox, QSlider,QFrame
from ui.SizeHelper import toDp
import cv2
from utils.yolov5_onnx import YOLOv5
from utils.BWJRoomHelperV2 import roomHelper
from utils.ButtonHelper import buttonHelper
import utils.RuntimeData as R
from config import SHOW_MAP_POINT, SHOW_BUTTON, ALPHA


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.onSizeChanged)
        self.sizeChanging = False
        self.lastPixmap = None
        self.drawMapPoint = True if SHOW_MAP_POINT else False
        self.drawButton = True if SHOW_BUTTON else False
        self.rightBarWidth = toDp(120)
        self.hSpace = toDp(3)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Window')
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
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.startBtn = QPushButton("start")
        self.startBtn.clicked.connect(self.onclick)
        self.resetBtn = QPushButton("reset")
        self.resetBtn.clicked.connect(self.onclick)
        self.checkBoxPoint = QCheckBox('地图锚点', self)
        self.checkBoxPoint.stateChanged.connect(self.onCheckBoxChanged)
        self.checkBoxButtons = QCheckBox('技能按钮', self)
        self.checkBoxButtons.stateChanged.connect(self.onCheckBoxChanged)
        self.slider = QSlider()
        self.slider.valueChanged.connect(self.onSliderChanged)
        self.labelAlpha = QLabel('')


        vbox = QVBoxLayout()
        vbox.addWidget(self.startBtn)
        vbox.addWidget(self.resetBtn)
        vbox.addWidget(self.checkBoxPoint)
        vbox.addWidget(self.checkBoxButtons)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.labelAlpha)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addWidget(vline)
        hbox.addWidget(spacer)
        hbox.addLayout(vbox)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.setContentsMargins(0, 0, 0, 0)
        # self.label.setScaledContents(True)
        self.label.resize(1000, 450)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.checkBoxPoint.setChecked(self.drawMapPoint)
        self.checkBoxButtons.setChecked(self.drawButton)
        self.slider.setOrientation(1)  # 设置为垂直方向
        self.slider.setRange(1, 100)
        self.slider.setValue(alpha)
        self.slider.setTickPosition(2)  # 设置刻度位置
        self.labelAlpha.setAlignment(Qt.AlignCenter)  # 设置文字居中显示

        btnWidth = self.rightBarWidth
        btnHeight = toDp(30)
        self.startBtn.setFixedSize(btnWidth, btnHeight)
        self.resetBtn.setFixedSize(btnWidth, btnHeight)
        self.checkBoxPoint.setFixedSize(btnWidth, btnHeight)
        self.checkBoxButtons.setFixedSize(btnWidth, btnHeight)
        self.slider.setFixedSize(btnWidth, btnHeight)
        self.labelAlpha.setFixedSize(btnWidth, btnHeight)

        self.setLayout(hbox)

    def resizeToDefault(self):
        self.setGeometry(100, 100, R.WINDOW_WIDTH+self.rightBarWidth+self.hSpace,
                         int(R.WINDOW_WIDTH*R.RATE))

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

            image = QImage(
                frame,
                frame.shape[1],
                frame.shape[0],
                frame.shape[1] * 3,
                QImage.Format_BGR888,
            )
            pix = QPixmap(image)
            pix = self.__resizePixmap(pix)
            self.label.setPixmap(pix)
            self.lastPixmap = pix

    def __resizePixmap(self, pix: QPixmap):
        rate = R.RATE
        labelRate = self.label.size().height()/self.label.size().width()
        if labelRate < rate:
            height = self.label.size().height()
            width = int(height / rate)
        else:
            width = self.label.size().width()
            height = int(width * rate)
        return pix.scaled(width, height, Qt.KeepAspectRatio)

    def onclick(self):
        if self.sender() is self.startBtn:
            if self.startBtn.text() == "start":
                self.startBtn.setText("stop")
                self.action.stop_event = False
            else:
                self.startBtn.setText("start")
                self.action.stop_event = True
        elif self.sender() is self.resetBtn:
            self.action.reset()

    def onCheckBoxChanged(self, state):
        if self.sender() is self.checkBoxPoint:
            self.drawMapPoint = True if state == 2 else False
        elif self.sender() is self.checkBoxButtons:
            self.drawButton = True if state == 2 else False

    def onSliderChanged(self):
        value = self.slider.value()
        self.labelAlpha.setText(f'透明度:{value}%')
        self.setWindowOpacity(value/100)

    def setComponents(self, client, yolo, action):
        self.client = client
        self.yolo = yolo
        self.action = action

    def paintEvent(self, event):
        pass

    def resizeEvent(self, event):
        if event.oldSize().width() != -1:
            self.timer.start(500)

        pix = self.lastPixmap
        if pix is not None:
            pix = self.__resizePixmap(pix)
            self.label.setPixmap(pix)

    def onSizeChanged(self):
        self.timer.stop()

    def closeEvent(self, event):
        self.yolo.stop()
        self.client.stop()
        self.action.quit()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    t = MainWindow()
    t.show()
    app.exec_()
