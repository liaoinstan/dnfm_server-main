

import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT
from component.action.ActionManager import actionManager


class AdvertAction(BaseAction):

    class Path(Enum):
        WT = 'way_to_bwj/wt.jpg', (0.8, 1, 0, 1)
        CLOSE1 = 'advert/close1.jpg', None
        CLOSE2 = 'advert/close2.jpg', None

        def __init__(self, path, area):
            self.path = path
            self.area = area

    closeBtnList = [Path.CLOSE1, Path.CLOSE2]

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

        resultClose = None
        for closeBtn in AdvertAction.closeBtnList:
            result = self.match(image, closeBtn)
            if result is not None:
                resultClose = result
                break

        # resultClose1 = self.match(image, AdvertAction.Path.CLOSE1)
        resultWt = self.match(image, AdvertAction.Path.WT)
        if resultWt and not resultClose:
            self.count += 1
            if self.count == 3:
                self.stop()
                print("活动广告清除完毕")
                # 活动广告清除完毕，开始上班
                actionManager.goToWorkAction.start()

        if resultClose:
            print("检测到活动广告弹窗，关闭。")
            self.count = 0
            self.click(resultClose)
            time.sleep(random.uniform(0.8, 1.2))

        time.sleep(0.3)
        return True
