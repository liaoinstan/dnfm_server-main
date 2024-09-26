

import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT
from component.action.ActionManager import actionManager


class AdvertAction(BaseAction):

    class Path(Enum):
        WT = 'way_to_bwj/wt.jpg'
        CLOSE1 = 'advert/close1.jpg'

    def getPathEnum(self):
        return AdvertAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False
        self.count = 0

    def start(self):
        self.runing = True
        
    def stop(self):
        self.removeAllResults()
        self.runing = False

    def actionCloseAdvert(self, image):
        if not self.runing:
            return False
        
        resultClose1 = self.match(image, AdvertAction.Path.CLOSE1.value)
        resultWt = self.match(image, AdvertAction.Path.WT.value)
        if resultWt and not resultClose1:
            self.count += 1
            if self.count == 3:
                self.stop()
                print("活动广告清除完毕")
                # 活动广告清除完毕，开始上班
                actionManager.goToWorkAction.start()
            
        if resultClose1:
            print("检测到活动广告弹窗，关闭。")
            self.count = 0
            self.click(resultClose1)
            time.sleep(random.uniform(0.8, 1.2))

        time.sleep(0.3)
        return True
