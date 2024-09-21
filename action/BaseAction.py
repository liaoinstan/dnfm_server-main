from abc import abstractmethod
from game_control import GameControl
import utils.MatchHelper as MatchHelper


class BaseAction:
    
    def __init__(self, ctrl, matchResultMap: dict):
        self.ctrl:GameControl = ctrl
        self.matchResultMap = matchResultMap
        
    @abstractmethod
    def getPathEnum(self):
        pass
    
    def match(self, image, path, showRect=True):
        result = MatchHelper.match_template(image, path)
        if showRect and result is not None:
            self.updateMatchResultMap({path: [result]})
        else:
            self.updateMatchResultMap({})
        return result

    def click(self, result):
        self.ctrl.click(result[0], result[1], convert=False)
        
    def updateMatchResultMap(self, resultMap: dict):
        # for key,value in resultMap.items():
        #     if value is None:
        #         self.matchResultMap.pop(key, None)
        #     else:
        #         self.matchResultMap[key] = value
        for enumName, enum in self.getPathEnum().__members__.items():
            if enum.value in resultMap and resultMap[enum.value] is not None:
                self.matchResultMap[enum.value] = resultMap[enum.value]
            else:
                self.matchResultMap.pop(enum.value, None)