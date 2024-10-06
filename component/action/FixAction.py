import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT


class FixAction(BaseAction):

    class Path(Enum):
        BACKPACK = 'fix/fix_backpack.jpg', (0.5, 0.8, 0, 0.33)
        BACKPACK_OVER = 'fix/fix_backpack_over.jpg', (0.5, 0.8, 0, 0.33)
        FIX_IRON_FELT = 'fix/fix_iron_felt.jpg', (0.33, 0, 66, 0, 8, 1)
        FIX_BTN_XL = 'fix/fix_btn_xl.jpg', (0.5, 1, 0.66, 1)
        FIX_CLOSE = 'fix/fix_close.jpg', (0.66, 1, 0, 0.25)
        FIX_BACK = 'fix/fix_back.jpg', (0, 0.25, 0, 0.25)

        def __init__(self, path, area):
            self.path = path
            self.area = area

    def getPathEnum(self):
        return FixAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False
        self.step = 0

    def start(self):
        self.reset()
        self.runing = True

    def stop(self):
        self.reset()
        self.removeAllResults()
        self.runing = False

    def reset(self):
        self.step = 0

    def actionFix(self, image):
        if not self.runing:
            return False
        if self.step == 0:
            resultBackpack = self.match(image, FixAction.Path.BACKPACK)
            print("自动维修装备")
            if resultBackpack:
                self.click(resultBackpack)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 1
            else:
                resultBackpackOver = self.match(image, FixAction.Path.BACKPACK_OVER)
                if resultBackpackOver:
                    self.click(resultBackpackOver)
                    time.sleep(random.uniform(0.8, 1.2))
                    self.step = 1
            time.sleep(0.3)
        elif self.step == 1:
            resultIronFelt = self.match(image, FixAction.Path.FIX_IRON_FELT)
            if resultIronFelt:
                self.click(resultIronFelt)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 2
            time.sleep(0.3)
        elif self.step == 2:
            resultBtnXl = self.match(image, FixAction.Path.FIX_BTN_XL)
            if resultBtnXl:
                self.click(resultBtnXl)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 3
            time.sleep(0.3)
        elif self.step == 3:
            resultFixClose = self.match(image, FixAction.Path.FIX_CLOSE)
            if resultFixClose:
                self.click(resultFixClose)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 4
            time.sleep(1)
        elif self.step == 4:
            resultBack = self.match(image, FixAction.Path.FIX_BACK)
            if resultBack:
                self.click(resultBack)
                time.sleep(random.uniform(0.8, 1.2))
                self.stop()
        return True
