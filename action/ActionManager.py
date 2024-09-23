from abc import abstractmethod
from game_control import GameControl
import utils.MatchHelper as MatchHelper
from action.GoToWorkAction import GoToWorkAction
from action.FixAction import FixAction
from action.ChangeHeroAction import ChangeHeroAction
from action.AgainAction import AgainAction
import utils.RuntimeData as R


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
        self.goToWorkAction: GoToWorkAction
        self.changeHeroAction: ChangeHeroAction
        self.fixAction: FixAction
        self.againAction: AgainAction
        self.image = None

    def init(self, goToWorkAction: GoToWorkAction, changeHeroAction: ChangeHeroAction, fixAction: FixAction, againAction: AgainAction):
        self.goToWorkAction = goToWorkAction
        self.changeHeroAction = changeHeroAction
        self.fixAction = fixAction
        self.againAction = againAction

    def start(self):
        if MatchHelper.match_template(self.image, 'way_to_bwj/wt.jpg'):
            # 副本外
            if R.CURRENT_HERO:
                print("当前角色:", R.CURRENT_HERO, "开始刷图")
                self.goToWorkAction.start()
            else:
                if R.nextHero():
                    print("当前角色未定义，准备切换角色")
                    self.changeHeroAction.start()
                else:
                    print("设定的角色疲劳已全部耗尽,停止脚本")
                    self.stopAllAction()
                    return

        elif MatchHelper.match_template(self.image, 'change_hero/hero_tag.jpg'):
            # 角色选择界面
            print("切换角色界面")
            self.changeHeroAction.start(2)

        else:
            # 副本内
            print("副本内,准备战斗")
            self.goToWorkAction.stop()
            self.changeHeroAction.stop()
            return
        
    def stopAllAction(self):
        self.goToWorkAction.stop()
        self.changeHeroAction.stop()
        self.fixAction.stop()
        self.dialogAction.stop()
        


actionManager = ActionManager()
