import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()

        label1 = QLabel('Label 1')
        vbox.addWidget(label1)

        # 添加一个固定大小的空白区域
        spacer = QWidget()
        spacer.setFixedSize(100, 50)
        vbox.addWidget(spacer)

        label2 = QLabel('Label 2')
        vbox.addWidget(label2)

        # 添加一个可伸缩的空白区域
        stretch = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox.addItem(stretch)

        self.setLayout(vbox)

        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('Add Blank Area Example')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
