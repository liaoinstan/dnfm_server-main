from abc import abstractmethod
from game_control import GameControl
import utils.MatchHelper as MatchHelper
import datetime
import cv2


class BaseAction:
    
    '''
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
    
    def match(self, image, path, showRect=True):
        result = MatchHelper.match_template(image, path)
        if showRect and result is not None:
            self.updateMatchResultMap({path: [result]})
        else:
            self.updateMatchResultMap({})
            
        # if path == 'way_to_bwj/loading.jpg':
        #     currentTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
        #     fileName = f'screenshot_{currentTime}.jpg'
        #     print(fileName, result)
        #     cv2.imwrite(f'screenshort/{fileName}',image)
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
                
    def removeAllResults(self):
        self.updateMatchResultMap({})