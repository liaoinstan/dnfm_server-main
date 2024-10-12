import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT


class FixAction(BaseAction):

    class Path(Enum):
        BACKPACK = 'fix/fix_backpack.jpg', (0.5, 0.8, 0, 0.33)
        BACKPACK_OVER = 'fix/fix_backpack_over.jpg', (0.5, 0.8, 0, 0.33)
        FIX_IRON_FELT = 'fix/fix_iron_felt.jpg', (0.33, 0.66, 0.8, 1)
        FIX_CHECK_CDZB = 'fix/fix_check_cdzb.jpg', (0, 0.5, 0.66, 1)
        FIX_BTN_XL = 'fix/fix_btn_xl.jpg', (0.5, 1, 0.66, 1)
        FIX_CLOSE = 'fix/fix_close.jpg', (0.66, 1, 0, 0.25)
        FIX_BACK = 'fix/fix_back.jpg', (0, 0.25, 0, 0.25)
        # 出售分解模版定义
        FIX_SALE_OPEN = 'fix/fix_sale_open.jpg', (0.75, 1, 0.8, 1)
        FIX_FJ_OPEN = 'fix/fix_fj_open.jpg', (0.75, 1, 0.8, 1)
        FIX_SALE = 'fix/fix_sale.jpg', (0.6, 0.9, 0.66, 1)
        FIX_FJ = 'fix/fix_FJ.jpg', (0.6, 0.9, 0.66, 1)
        FIX_CHECK_BAI = 'fix/fix_check_bai.jpg', (0.2, 0.8, 0.66, 1)
        FIX_CHECK_LAN = 'fix/fix_check_lan.jpg', (0.2, 0.8, 0.66, 1)
        FIX_CHECK_ZI = 'fix/fix_check_zi.jpg', (0.2, 0.8, 0.66, 1)
        COM_YES = 'common/com_yes.jpg', (0.33, 0.66, 0.33, 0.8)

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
            resultCheckCDZB = self.match(image, FixAction.Path.FIX_CHECK_CDZB)
            if resultCheckCDZB:
                self.click(resultCheckCDZB)
                time.sleep(random.uniform(0.8, 1.2))
            else:
                time.sleep(0.5)
            self.step = 3
        elif self.step == 3:
            resultBtnXl = self.match(image, FixAction.Path.FIX_BTN_XL)
            if resultBtnXl:
                self.click(resultBtnXl)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 4
            time.sleep(0.3)
        elif self.step == 4:
            resultFixClose = self.match(image, FixAction.Path.FIX_CLOSE)
            if resultFixClose:
                self.click(resultFixClose)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 4.1
            time.sleep(0.5)
        elif 4 < self.step < 5:
            self.__actionSale(image)
        elif 5 < self.step < 6:
            self.__actionFJ(image)
        elif self.step == 6:
            print("关闭背包")
            resultBack = self.match(image, FixAction.Path.FIX_BACK)
            if resultBack:
                self.click(resultBack)
                time.sleep(random.uniform(0.8, 1.2))
                self.stop()
        return True

    # 子Action, 出售装备
    def __actionSale(self, image):
        if self.step == 4.1:
            result = self.match(image, FixAction.Path.FIX_SALE_OPEN)
            if result:
                print("自动出售装备（蓝紫）")
                self.click(result)
                time.sleep(1.5)
                self.step = 4.2
            time.sleep(0.3)
        elif self.step == 4.2:
            resultChecklan = self.match(image, FixAction.Path.FIX_CHECK_LAN, threshold=0.85)
            if resultChecklan:
                print("勾选蓝装")
                self.click(resultChecklan, biasH=0.25)
                time.sleep(random.uniform(0.8, 1.2))
            else:
                print("蓝装已勾选")
                resultCheckZi = self.match(image, FixAction.Path.FIX_CHECK_ZI, threshold=0.85)
                if resultCheckZi:
                    print("勾选紫装")
                    self.click(resultCheckZi, biasH=0.25)
                    time.sleep(random.uniform(0.8, 1.2))
                else:
                    print("紫色已勾选")
                    self.step = 4.3
            time.sleep(0.3)
        elif self.step == 4.3:
            resultFixSale = self.match(image, FixAction.Path.FIX_SALE)
            if resultFixSale:
                print("点击出售按钮")
                self.click(resultFixSale)
                time.sleep(1.5)
                self.step = 4.4
            time.sleep(0.3)
        elif self.step == 4.4:
            resultYes = self.match(image, FixAction.Path.COM_YES)
            if resultYes:
                print("确认弹窗")
                self.click(resultYes)
                time.sleep(1.5)
            else:
                print("准备关闭出售页面")
                self.step = 4.5
            time.sleep(0.3)
        elif self.step == 4.5:
            # 右上角的'X'
            resultFixClose = self.match(image, FixAction.Path.FIX_CLOSE)
            if resultFixClose:
                self.click(resultFixClose)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 5.1
            time.sleep(0.5)

    # 子Action, 分解装备
    def __actionFJ(self, image):
        if self.step == 5.1:
            result = self.match(image, FixAction.Path.FIX_FJ_OPEN)
            if result:
                print("自动分解装备（白）")
                self.click(result)
                time.sleep(1.5)
                self.step = 5.2
            time.sleep(0.3)
        elif self.step == 5.2:
            resultCheckBai = self.match(image, FixAction.Path.FIX_CHECK_BAI, threshold=0.85)
            if resultCheckBai:
                print("勾选白装", resultCheckBai[4])
                self.click(resultCheckBai, biasH=0.25)
                time.sleep(random.uniform(0.8, 1.2))
            else:
                print("白装已勾选")
                self.step = 5.3
            time.sleep(0.3)
        elif self.step == 5.3:
            result = self.match(image, FixAction.Path.FIX_FJ)
            if result:
                print("点击分解按钮")
                self.click(result)
                time.sleep(1.5)
                self.step = 5.4
            time.sleep(0.3)
        elif self.step == 5.4:
            resultYes = self.match(image, FixAction.Path.COM_YES)
            if resultYes:
                print("确认弹窗")
                self.click(resultYes)
                time.sleep(1.5)
            else:
                print("准备关闭分解页面")
                self.step = 5.5
            time.sleep(0.3)
        elif self.step == 5.5:
            # 右上角的'X'
            resultFixClose = self.match(image, FixAction.Path.FIX_CLOSE)
            if resultFixClose:
                self.click(resultFixClose)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 6
            time.sleep(0.5)
