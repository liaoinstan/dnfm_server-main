

import random
import time
from action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT


class FixAction(BaseAction):

    class Path(Enum):
        BACKPACK = 'fix/fix_backpack.jpg'
        FIX_IRON_FELT = 'fix/fix_iron_felt.jpg'
        FIX_BTN_XL = 'fix/fix_btn_xl.jpg'
        FIX_CLOSE = 'fix/fix_close.jpg'
        FIX_BACK = 'fix/fix_back.jpg'

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
            resultBackpack = self.match(image, FixAction.Path.BACKPACK.value)
            print("自动维修装备")
            if resultBackpack:
                self.click(resultBackpack)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 1
            time.sleep(0.3)
        elif self.step == 1:
            resultIronFelt = self.match(image, FixAction.Path.FIX_IRON_FELT.value)
            if resultIronFelt:
                self.click(resultIronFelt)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 2
            time.sleep(0.3)
        elif self.step == 2:
            resultBtnXl = self.match(image, FixAction.Path.FIX_BTN_XL.value)
            if resultBtnXl:
                self.click(resultBtnXl)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 3
            time.sleep(0.3)
        elif self.step == 3:
            resultFixClose = self.match(image, FixAction.Path.FIX_CLOSE.value)
            if resultFixClose:
                self.click(resultFixClose)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 4
            time.sleep(1)
        elif self.step == 4:
            resultBack = self.match(image, FixAction.Path.FIX_BACK.value)
            if resultBack:
                self.click(resultBack)
                time.sleep(random.uniform(0.8, 1.2))
                self.stop()
        return True
