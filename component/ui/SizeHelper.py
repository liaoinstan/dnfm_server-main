from PyQt5.QtWidgets import QApplication


class SizeHelper(object):

    def __init__(self):
        self.designDpi = 144
        self.dpi = 0

    def calDpi(self):
        desktop = QApplication.desktop()
        if desktop is not None:
            dpiX = desktop.logicalDpiX()
            dpiY = desktop.logicalDpiY()
            print("dpiX", dpiX, "dpiY", dpiY)
            self.dpi = (dpiX + dpiY) / 2

    def getDpi(self):
        if self.dpi == 0:
            self.calDpi()
        return self.dpi

    def toDp(self, px):
        dpi = self.getDpi()
        if dpi == 0:
            return px
        else:
            return int(px / self.designDpi * dpi)


sizeHelper = SizeHelper()


def toDp(px):
    return sizeHelper.toDp(px)


if __name__ == '__main__':
    print('''aaa %s bbb''' % (1))
