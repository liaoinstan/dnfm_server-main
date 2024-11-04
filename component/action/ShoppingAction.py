
import component.utils.MatchHelper as MatchHelper
import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
import component.utils.RuntimeData as R


class ShoppingAction(BaseAction):

    class Path(Enum):
        SHOPPING_ENTER = 'shopping/shopping_enter.jpg', (0.6, 0.9, 0, 0.3)
        SHOPPING_STAR = 'shopping/shopping_star.jpg', (0, 0.25, 0.5, 1)
        SHOPPING_BUY = 'shopping/shopping_buy.jpg', (0.66, 1, 0.66, 1)
        SHOPPING_EXIT = 'shopping/shopping_exit.jpg', (0, 0.25, 0, 0.25)
        COM_YES = 'common/com_yes.jpg', (0.33, 0.8, 0.5, 0.9)
        WT = 'way_to_bwj/wt.jpg', (0.8, 1, 0, 1)

        def __init__(self, path, area):
            self.path = path
            self.area = area

    def getPathEnum(self):
        return ShoppingAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False
        self.step = 0
        self.onShoppingEndCallback = None

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
        
    def onShoppingEnd(self, onShoppingEndCallback):
        self.onShoppingEndCallback = onShoppingEndCallback

    def actionShopping(self, image):
        if not self.runing:
            return False
        if self.step == 0:
            result = self.match(image, ShoppingAction.Path.SHOPPING_ENTER)
            if result:
                self.click(result)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 1
            time.sleep(0.5)
        elif self.step == 1:
            x1, y1 = R.DEVICE_WIDTH*0.1, R.DEVICE_HEIGHT*0.6
            x2, y2 = R.DEVICE_WIDTH*0.1, R.DEVICE_HEIGHT*0.4
            self.ctrl.adb.touch_swipe(x1, y1, x2, y2, 10, 0.05)
            time.sleep(random.uniform(0.8, 1.2))
            result = self.match(image, ShoppingAction.Path.SHOPPING_STAR)
            if result:
                self.click(result)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 2
            else:
                time.sleep(1)
        elif self.step == 2:
            result = self.match(image, ShoppingAction.Path.SHOPPING_BUY)
            if result:
                self.click(result)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 3
            time.sleep(0.8)
        elif self.step == 3:
            result = self.match(image, ShoppingAction.Path.COM_YES)
            if result:
                self.click(result)
                time.sleep(random.uniform(1.2, 1.5))
            else:
                self.step = 4
                time.sleep(1)
        elif self.step == 4:
            resultWT = self.match(image, ShoppingAction.Path.WT)
            if resultWT:
                time.sleep(0.5)
                self.stop()
                print("购买完毕,退出商城")
                if self.onShoppingEndCallback:
                    self.onShoppingEndCallback()
            else:
                resultExit = self.match(image, ShoppingAction.Path.SHOPPING_EXIT)
                if resultExit:
                    self.click(resultExit)
                    time.sleep(0.8)
            time.sleep(0.5)
        return True
