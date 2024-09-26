
import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT
import component.utils.RuntimeData as R
from component.action.ActionManager import actionManager


class GoToWorkAction(BaseAction):

    class Path(Enum):
        ZERO = 'way_to_bwj/zero.jpg'
        WT = 'way_to_bwj/wt.jpg'
        MAP_TAB = 'way_to_bwj/map_tab.jpg'
        MAP_WNXS = 'way_to_bwj/map_wnxs.jpg'
        SELECT_MX = 'way_to_bwj/select_mx.jpg'
        SELECT_BWJ = 'way_to_bwj/select_bwj.jpg'
        SELECT_START = 'way_to_bwj/select_start.jpg'
        LOADING = 'way_to_bwj/loading.jpg'
        NOT_SHOW = 'dialog/dialog_not_show.jpg'
        YES = 'dialog/dialog_yes.jpg'

    def getPathEnum(self):
        return GoToWorkAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.timeOut = 0
        self.runing = False
        self.step = -1

    def start(self):
        self.reset()
        self.runing = True

    def stop(self):
        self.reset()
        self.removeAllResults()
        self.runing = False

    def reset(self):
        self.timeOut = 0
        self.step = -1

    def actionWayToBWJ(self, image):
        if not self.runing:
            return False

        if self.step == -1:
            # 超过10秒没检测到标志，自动取消寻路流程
            if self.timeOut != 0:
                waitTime = int((time.time() - self.timeOut) * 1000)
                if waitTime > 10000:
                    print("取消自动寻路")
                    self.stop()
            resultWt = self.match(image, GoToWorkAction.Path.WT.value)
            if resultWt:
                self.ctrl.click(CENTER_POINT[0], CENTER_POINT[1])
                time.sleep(0.5)
                self.ctrl.click(CENTER_POINT[0], CENTER_POINT[1])
                time.sleep(0.5)
                self.step = 0
            else:
                if self.timeOut == 0:
                    self.timeOut = time.time()
            time.sleep(0.3)
        if self.step == 0:
            resultMapWnxs = self.match(image, GoToWorkAction.Path.MAP_WNXS.value)
            if resultMapWnxs:
                self.click(resultMapWnxs)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 1
            else:
                resultMapTab = self.match(image, GoToWorkAction.Path.MAP_TAB.value)
                if resultMapTab:
                    self.click(resultMapTab)
                    time.sleep(random.uniform(0.8, 1.2))
            time.sleep(0.3)
        elif self.step == 1:
            print("正在前往布万加")
            resultSelectMX = self.match(image, GoToWorkAction.Path.SELECT_MX.value)
            if resultSelectMX:
                print("点击冒险模式")
                self.click(resultSelectMX)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 2
            time.sleep(1)
        elif self.step == 2:
            resultSelectBwj = self.match(image, GoToWorkAction.Path.SELECT_BWJ.value)
            if resultSelectBwj:
                print("点击布万加")
                self.click(resultSelectBwj)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 3
            time.sleep(0.3)
        elif self.step == 3:
            resultSelectStart = self.match(image, GoToWorkAction.Path.SELECT_START.value)
            if resultSelectStart:
                print("点击开始")
                self.click(resultSelectStart)
                time.sleep(0.5)
                self.step = 4
            time.sleep(0.3)
        elif self.step == 4:
            resultLoading = self.match(image, GoToWorkAction.Path.LOADING.value, showRect=False)
            if resultLoading:
                print("加载中...")
                self.stop()
            else:
                resultYes = self.match(image, GoToWorkAction.Path.YES.value)
                if resultYes:
                    print("检测到弹窗，关闭")
                    time.sleep(random.uniform(0.8, 1.2))
                    resultCheckBox = self.match(image, GoToWorkAction.Path.NOT_SHOW.value)
                    if resultCheckBox:
                        time.sleep(random.uniform(0.8, 1.2))
                        self.click(resultCheckBox)
                    time.sleep(random.uniform(0.8, 1.2))
                    self.click(resultYes)
                    self.step = 5
                time.sleep(0.1)
        elif self.step == 5:
            resultLoading = self.match(image, GoToWorkAction.Path.LOADING.value, showRect=False)
            if resultLoading:
                print("加载中...")
                self.stop()
        return True
