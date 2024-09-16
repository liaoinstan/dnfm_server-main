import sys

from PyQt5.QtCore import Qt, QPoint, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QPainterPath, QPainter, QBrush, QColor, QMouseEvent, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout
from ui.SizeHelper import toDp
import cv2
from utils.yolov5_onnx import YOLOv5
from utils.BWJRoomHelperV2 import roomHelper, Direction
from utils.ButtonHelper import buttonHelper


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Window')
        self.setGeometry(100, 100, 800, 400)
        self.setWindowOpacity(0.75)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.startBtn = QPushButton("start")
        self.startBtn.clicked.connect(self.onclick)
        self.resetBtn = QPushButton("reset")
        self.resetBtn.clicked.connect(self.onclick)

        vbox = QVBoxLayout()
        vbox.addWidget(self.startBtn)
        vbox.addWidget(self.resetBtn)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addLayout(vbox)
        hbox.setContentsMargins(0, 0, 0, 0)

        btnWidth = toDp(100)
        btnHeight = toDp(30)
        self.startBtn.setFixedSize(btnWidth, btnHeight)
        self.resetBtn.setFixedSize(btnWidth, btnHeight)

        self.setLayout(hbox)

    def onFrame(self, frame, output):
        if frame is not None:

            for boxs in output:
                det_x1, det_y1, det_x2, det_y2, conf, label = boxs
                x1 = int(det_x1*frame.shape[1])
                y1 = int(det_y1*frame.shape[0])
                x2 = int(det_x2*frame.shape[1])
                y2 = int(det_y2*frame.shape[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "{:.2f}".format(conf), (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, YOLOv5.label[int(label)], (int(x1), int(y1-30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            roomHelper.drawMap(frame)
            roomHelper.drawMiniMap(frame)
            # buttonHelper.drawButtons(image, control.config)

            image = QImage(
                frame,
                frame.shape[1],
                frame.shape[0],
                frame.shape[1] * 3,
                QImage.Format_BGR888,
            )
            pix = QPixmap(image)
            self.label.setPixmap(pix)

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

    def setAction(self, action):
        self.action = action

    def paintEvent(self, event):
        pass

    def resizeEvent(self, event):
        new_width = event.size().width()
        new_height = event.size().height()
        if new_height != new_width / 2:
            if new_height > new_width / 2:
                new_height = new_width / 2
            else:
                new_width = new_height * 2
            self.resize(new_width, new_height)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    t = MainWindow()
    t.show()
    app.exec_()
