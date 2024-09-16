import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainterPath, QPainter, QBrush, QColor, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget
if __name__ == '__main__':
    from SizeHelper import toDp
else:
    from .SizeHelper import toDp


class RoundShadow(QWidget):
    """圆角边框类"""

    def __init__(self, parent=None):
        super(RoundShadow, self).__init__(parent)
        # self.border_width = toDp(8)
        # self.round_width = toDp(6)
        # self.border_width = 8
        # self.round_width = 6
        # 设置 窗口无边框和背景透明 *必须
        # self.setWindowOpacity(0.85)  # 设置窗口透明度
        # self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框，置顶| Qt.WindowStaysOnTopHint
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        # 阴影
        # path = QPainterPath()
        # path.setFillRule(Qt.WindingFill)

        # pat = QPainter(self)
        # pat.setRenderHint(pat.Antialiasing)
        # pat.fillPath(path, QBrush(QColor(0, 0, 0)))

        # 圆角
        pat2 = QPainter(self)
        pat2.setRenderHint(pat2.Antialiasing)  # 抗锯齿
        pat2.setBrush(QColor(0, 0, 0, 88))
        pat2.setPen(Qt.transparent)

        rect = self.rect()
        rect.setLeft(1)
        rect.setTop(1)
        rect.setWidth(rect.width() - 1)
        rect.setHeight(rect.height() - 1)
        #pat2.drawRoundedRect(rect, self.round_width, self.round_width)
        pat2.drawRect(rect)

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        if e.pos() is None or not hasattr(self, "_startPos") or self._startPos is None:
            return
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None


if __name__ == '__main__':
    class MyWindow(RoundShadow, QWidget):
        """测试窗口"""

        def __init__(self, parent=None):
            super(MyWindow, self).__init__(parent)
            self.resize(300, 300)


    app = QApplication(sys.argv)
    t = MyWindow()
    # t = RoundImage('./Asset/new_icons/close.png')
    t.show()
    app.exec_()
