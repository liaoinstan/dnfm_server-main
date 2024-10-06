import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QPainter,  QFont, QColor,  QTransform, QPen, QFontMetrics
from PyQt5.QtWidgets import QLabel
import numpy as np

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 1000, 1000)
        self.setWindowTitle('PyQt Button Example')
        
        
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.__drawArrow(painter,50,50,100,200)
        painter.end()
        
    def __drawArrow(self, painter,x1, y1, x2, y2):
        def calcuArrow(x1, y1, x2, y2, arrowRate: float=0, arrowSize: int=0):
            if arrowSize != 0:
                size = arrowSize
            elif arrowRate != 0:
                lengthLine = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                size = int(lengthLine * arrowRate)
            else:
                size = 20
            length = 0  # 圆点距离终点图元的距离
            k = math.atan2(y2 - y1, x2 - x1)  # theta
            new_x = x2 - length * math.cos(k)  # 减去线条自身的宽度
            new_y = y2 - length * math.sin(k)
            new_x1 = new_x - size * math.cos(k - np.pi / 6)
            new_y1 = new_y - size * math.sin(k - np.pi / 6)
            new_x2 = new_x - size * math.cos(k + np.pi / 6)
            new_y2 = new_y - size * math.sin(k + np.pi / 6)
            point1 = (new_x, new_y)
            point2 = (new_x1, new_y1)
            point3 = (new_x2, new_y2)
            return point1, point2, point3
        arrowPonit1, arrowPonit2, arrowPonit3 = calcuArrow(x1, y1, x2, y2, arrowRate=0.1)
        painter.setBrush(Qt.red)
        painter.setPen(QColor(255,0,0))
        painter.drawLine(x1, y1, x2, y2)
        painter.drawPolygon(QPoint(arrowPonit1[0], arrowPonit1[1]), QPoint(arrowPonit2[0], arrowPonit2[1]), QPoint(arrowPonit3[0], arrowPonit3[1]))
        

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
