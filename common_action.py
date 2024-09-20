
import utils.MatchHelper as MatchHelper
import random
import time

class CommonAction:
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.battle_start = True
        self.battle_start2 = True
    
    def actionWayToBWJ(self, image):
        # 开局跑图逻辑：
        if battle_start:
            if battle_start2:
                # 点击委托 并点击移动到山脊：
                find_start, pos = MatchHelper.match_start(image)
                if find_start:
                    self.ctrl.click(pos[0], pos[1])
                    time.sleep(random.uniform(0.8, 1.2))
                    self.ctrl.click(self.ctrl.config["start_tab"][0], self.ctrl.config["start_tab"][1])
                    time.sleep(random.uniform(0.8, 1.2))
                    self.ctrl.click(self.ctrl.config["start_SJ"][0], self.ctrl.config["start_SJ"][1])
                    time.sleep(random.uniform(0.8, 1.2))
                    self.ctrl.click(self.ctrl.config["map_enter"][0], self.ctrl.config["map_enter"][1])
                    time.sleep(1.0)
                    battle_start2 = False
                else:
                    battle_start2 = False
                    battle_start = False
            else:
                find_start = MatchHelper.match_map(image)
                if find_start:
                    self.ctrl.click(self.ctrl.config["map_close"][0], self.ctrl.config["map_close"][1])
                    time.sleep(random.uniform(0.8, 1.2))
                    self.ctrl.click(self.ctrl.config["map_bwj"][0], self.ctrl.config["map_bwj"][1])
                    time.sleep(random.uniform(0.8, 1.2))
                    self.ctrl.click(self.ctrl.config["map_enter"][0], self.ctrl.config["map_enter"][1])
                    battle_start = False
                    time.sleep(1.0)
                else:
                    print(f"\r前往布万家的移动中....", end="")
    