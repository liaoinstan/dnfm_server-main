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
        self.ctrl: GameControl = ctrl
        self.matchResultMap = matchResultMap

    @abstractmethod
    def getPathEnum(self):
        pass

    def match(self, image, enum, showRect=True, threshold=0.7):
        result = MatchHelper.match_template(image, enum.path, area=enum.area, threshold=threshold)
        if showRect and result is not None:
            self.updateMatchResultMap({enum.path: [result]})
        else:
            self.updateMatchResultMap({})
        return result

    def click(self, result, biasH=0.5, biasV=0.5):
        '''
        点击一个匹配结果对应的区域
        biasH,biasV指点击位置相对于区域左上角的偏移,0为最左上,1为最右下,0.5为中心
        '''
        if biasH != 0.5:
            cx = result[0]
            w = result[2]
            x = int(cx - w/2 + w*biasH)
        else:
            x = result[0]
        if biasV != 0.5:
            cy = result[1]
            h = result[3]
            y = int(cy - h/2 + h*biasH)
        else:
            y = result[1]
        self.ctrl.click(x, y, ramdon=False, convert=False)

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
