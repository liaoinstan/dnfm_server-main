from abc import abstractmethod
from component.adb.game_control import GameControl
import component.utils.MatchHelper as MatchHelper


class BaseAction:
    '''
    Action 的基类，为子类提供公共方法和成员变量
    matchResultMap
    {
        "fix/fix_btn_xl.jpg" : [(cx,cy,w,h),(cx,cy,w,h)]
    }
    '''
    
    def __init__(self, ctrl, matchResultMap: dict):
        self.ctrl:GameControl = ctrl
        self.matchResultMap = matchResultMap
        
    @abstractmethod
    def getPathEnum(self):
        pass
    
    def match(self, image, enum, showRect=True):
        result = MatchHelper.match_template(image, enum.path)
        if showRect and result is not None:
            self.updateMatchResultMap({enum.path: [result]})
        else:
            self.updateMatchResultMap({})
        return result

    def click(self, result):
        '''
        点击一个匹配结果对应的区域中心位置
        '''
        self.ctrl.click(result[0], result[1], convert=False)
        
    def updateMatchResultMap(self, resultMap: dict):
        '''
        把匹配结果显示到屏幕上
        '''
        for enumName, enum in self.getPathEnum().__members__.items():
            if enum.path in resultMap and resultMap[enum.path] is not None:
                self.matchResultMap[enum.path] = resultMap[enum.path]
            else:
                self.matchResultMap.pop(enum.path, None)
                
    def removeAllResults(self):
        '''
        从屏幕上异常所有匹配结果
        '''
        self.updateMatchResultMap({})