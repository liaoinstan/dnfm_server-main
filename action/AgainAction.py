

import random
import time
from action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT
import utils.RuntimeData as R
from action.ActionManager import actionManager


class AgainAction(BaseAction):

    class Path(Enum):
        AGAIN = 'again/again.jpg'
        GOHOME = 'again/go_home.jpg'
        NOT_SHOW = 'dialog/dialog_not_show.jpg'
        YES = 'dialog/dialog_yes.jpg'
        LOADING = 'way_to_bwj/loading.jpg'
        WT = 'way_to_bwj/wt.jpg'

    def getPathEnum(self):
        return AgainAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False
        self.step = 0
        self.timeOut = 0
        self.clickedGoHome = False

    def start(self):
        self.reset()
        self.runing = True

    def stop(self):
        self.reset()
        self.removeAllResults()
        self.runing = False

    def reset(self):
        self.step = 0
        self.timeOut = 0
        self.clickedGoHome = False

    def actionAgain(self, image):
        if not self.runing:
            return False
        if self.timeOut != 0:
            waitTime = int((time.time() - self.timeOut) * 1000)
            if waitTime > 10000:
                if not self.clickedGoHome:
                    print("再次挑战超时，检测回城")
                    resultGoHome = self.match(image, AgainAction.Path.GOHOME.value)
                    if resultGoHome:
                        print("点击回城")
                        time.sleep(random.uniform(0.8, 1.2))
                        self.click(resultGoHome)
                        self.clickedGoHome = True
                        # 记录该英雄已完成
                        if R.CURRENT_HERO in R.HEROS:
                            R.HEROS[R.CURRENT_HERO] = True
                        time.sleep(1)
                    else:
                        print("异常：没有发现回城按钮")
                        self.stop()
                else:
                    resultWt = self.match(image, AgainAction.Path.WT.value)
                    if resultWt:
                        print("回到城镇")
                        self.stop()
                        time.sleep(0.3)
                        # 重新开启下一轮角色检查
                        actionManager.start()
                
        if self.step == 0:
            resultAgain = self.match(image, AgainAction.Path.AGAIN.value)
            if resultAgain:
                print("检测到再次挑战，点击")
                time.sleep(random.uniform(0.8, 1.2))
                self.click(resultAgain)
                # 开始计时
                if self.timeOut == 0:
                    self.timeOut = time.time()
                self.step = 1
            time.sleep(0.3)
        elif self.step == 1:
            if self.match(image, AgainAction.Path.LOADING.value, showRect=False):
                print("重新挑战")
                self.stop()
            else:
                resultYes = self.match(image, AgainAction.Path.YES.value)
                if resultYes:
                    print("检测到弹窗，关闭")
                    time.sleep(random.uniform(0.8, 1.2))
                    resultCheckBox = self.match(image, AgainAction.Path.NOT_SHOW.value)
                    if resultCheckBox:
                        time.sleep(random.uniform(0.8, 1.2))
                        self.click(resultCheckBox)
                    time.sleep(random.uniform(0.8, 1.2))
                    self.click(resultYes)
                    self.step = 2
            time.sleep(0.1)
        elif self.step == 2:
            if self.match(image, AgainAction.Path.LOADING.value, showRect=False):
                print("重新挑战")
                self.stop()
            time.sleep(0.1)

        return True
