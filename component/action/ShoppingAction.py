
import component.utils.MatchHelper as MatchHelper
import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
import component.utils.RuntimeData as R
from component.action.ActionManager import actionManager
from component.utils.EventManager import eventManager


class ShoppingAction(BaseAction):

    class Path(Enum):
        SHOPPING_ENTER = 'shopping/shopping_enter.jpg', None
        SHOPPING_STAR = 'shopping/shopping_star.jpg', None
        SHOPPING_BUY = 'shopping/shopping_buy.jpg', None
        SHOPPING_EXIT = 'shopping/shopping_exit.jpg', None
        COM_YES = 'common/com_yes.jpg', None

        def __init__(self, path, area):
            self.path = path
            self.area = area

    def getPathEnum(self):
        return ShoppingAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False
        self.step = 0

    def start(self, step=0):
        self.reset()
        self.step = step
        self.runing = True

    def stop(self):
        self.reset()
        self.removeAllResults()
        self.runing = False

    def reset(self):
        self.step = 0

    def actionShopping(self, image):
        if not self.runing:
            return False
        if self.step == 0:
            resultSetting = self.match(image, ShoppingAction.Path.HERO_SETTING)
            if resultSetting:
                self.click(resultSetting)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 1
            time.sleep(0.3)
        elif self.step == 1:
            resultChange = self.match(image, ShoppingAction.Path.HERO_CHANGE)
            if resultChange:
                self.click(resultChange)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 2
            time.sleep(0.3)

        return True
