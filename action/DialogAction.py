

import random
import time
from action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT


class DialogAction(BaseAction):

    class Path(Enum):
        NOT_SHOW = 'dialog/dialog_not_show.jpg'
        YES = 'dialog/dialog_yes.jpg'

    def getPathEnum(self):
        return DialogAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False

    def start(self):
        self.runing = True
        
    def stop(self):
        self.removeAllResults()
        self.runing = False

    def actionCloseDialog(self, image):
        if not self.runing:
            return False
        
        resultYes = self.match(image, DialogAction.Path.YES.value)
        if resultYes:
            print("检测到弹窗，关闭。")
            resultCheckBox = self.match(image, DialogAction.Path.NOT_SHOW.value)
            if resultCheckBox:
                time.sleep(random.uniform(0.8, 1.2))
                # self.click(resultCheckBox)
            time.sleep(random.uniform(0.8, 1.2))
            self.click(resultYes)
            time.sleep(random.uniform(1, 2))
            self.stop()
        else:
            print("未发现弹窗")

        return False
