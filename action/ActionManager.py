from abc import abstractmethod
from game_control import GameControl
import utils.MatchHelper as MatchHelper


class ActionManager:
    
    '''
    这个类用于管理不同的Action, 检查当前所处的环境,调度不同的action进行处理
    1.副本中：战斗通关
    2.副本外1.未知英雄疲劳状态，切换角色选择预设角色并获取疲劳状态
            2.已知疲劳状态: 1.疲劳未耗尽->执行刷本
                           2.疲劳已耗尽->切换角色
    所有预设角色疲劳全部耗尽,停止调度
    '''

    
    def __init__(self):
        pass
        
    