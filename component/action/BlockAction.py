

import random
import time
from component.adb.game_control import GameControl
from component.action.BaseAction import BaseAction
from enum import Enum
from config import CENTER_POINT
from component.action.ActionManager import actionManager


class BlockAction:

    def __init__(self, ctrl):
        self.ctrl:GameControl = ctrl
        self.timeOutBlock = 0
        self.timeOutRoom = 0
        
    def __isBlockTimeOut(self):
        if self.timeOutBlock == 0:
            return False
        return int((time.time() - self.timeOutBlock) * 1000) > 5000
    
    def __isRoomTimeOut(self):
        if self.timeOutRoom == 0:
            return False
        return int((time.time() - self.timeOutRoom) * 1000) > 30000

    def updatTimer(self):
        if self.timeOutBlock == 0:  
            self.timeOutBlock = time.time()
            
    def updatTimerWhenRoomTimeOut(self):
        if self.timeOutRoom == 0:
            self.timeOutRoom = time.time()
        if self.__isRoomTimeOut():
            self.updatTimer()

    def resetTimer(self):
        self.timeOutBlock = 0
        
    def resetRoomTimer(self):
        self.timeOutRoom = 0

    def actionCheckBlock(self):
        # 超时补救措施
        if self.__isBlockTimeOut():
            random_angle = random.randint(0, 360)
            print('\n检测到卡位,尝试脱离卡位,角度:',random_angle, end='\n')
            self.ctrl.attack(False) 
            self.ctrl.move(random_angle)
            time.sleep(1)
            self.resetTimer()
            return True
        return False
    
    def getWaitTime(self):
        if self.timeOutBlock == 0:
            return 0
        else:
            return int((time.time() - self.timeOutBlock) * 1000) 
