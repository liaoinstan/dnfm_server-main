from abc import abstractmethod
import component.utils.MatchHelper as MatchHelper
import component.utils.RuntimeData as R
from PyQt5.QtCore import QTimer
from component.utils.EventManager import eventManager


class ActionManager:

    '''
    这个类用于管理不同的Action, 检查当前所处的环境,调度不同的action进行处理
    1.副本中：战斗通关
    2.副本外--1.未知英雄疲劳状态，切换角色选择预设角色并获取疲劳状态
    ---------2.已知疲劳状态: 1.疲劳未耗尽->执行刷本
    ------------------------2.疲劳已耗尽->切换角色
    所有预设角色疲劳全部耗尽,停止调度
    '''

    def __init__(self):
        self.goToWorkAction = None
        self.changeHeroAction = None
        self.fixAction = None
        self.againAction = None
        self.advertAction = None
        self.image = None
        self.matchStartTimes = 0

    def init(self, goToWorkAction, changeHeroAction, fixAction, againAction, advertAction):
        self.goToWorkAction = goToWorkAction
        self.changeHeroAction = changeHeroAction
        self.fixAction = fixAction
        self.againAction = againAction
        self.advertAction = advertAction
        
    def reset(self):
        self.matchStartTimes = 0

    def start(self):
        print(f"开始：{self.matchStartTimes}")
        resultWt = MatchHelper.match_template(self.image, 'way_to_bwj/wt.jpg', area=(0.8, 1, 0, 1))
        if resultWt:
            # 副本外
            if R.CURRENT_HERO and not R.HEROS[R.CURRENT_HERO]:
                print("当前角色:", R.CURRENT_HERO, "开始刷图")
                self.goToWorkAction.start()
            else:
                if R.nextHero():
                    print("当前角色未定义，准备切换角色")
                    self.changeHeroAction.start()
                else:
                    print("设定的角色疲劳已全部耗尽,停止脚本")
                    self.stopAllAction()
                    eventManager.publish('FINISH_EVENT')
            self.reset()
        elif MatchHelper.match_template(self.image, 'change_hero/hero_tag.jpg'):
            # 角色选择界面
            print("切换角色界面")
            self.reset()
            self.changeHeroAction.start(2)
        else:
            self.matchStartTimes += 1
            if self.matchStartTimes <=3:
                timer = QTimer()
                timer.singleShot(500, self.start)
            else:
                # 副本内
                print("副本内,准备战斗")
                self.reset()
                self.goToWorkAction.stop()
                self.changeHeroAction.stop()
                return
            

    def stopAllAction(self):
        self.goToWorkAction.stop()
        self.changeHeroAction.stop()
        self.fixAction.stop()
        self.againAction.stop()
        self.advertAction.stop()


actionManager = ActionManager()
