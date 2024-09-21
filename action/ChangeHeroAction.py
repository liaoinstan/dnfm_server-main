
import utils.MatchHelper as MatchHelper
import random
import time
from action.BaseAction import BaseAction
from enum import Enum
import numpy as np


class ChangeHeroAction(BaseAction):

    class Path(Enum):
        HERO_SETTING = 'change_hero/hero_setting.jpg'
        HERO_CHANGE = 'change_hero/hero_change.jpg'
        HERO_TAG = 'change_hero/hero_tag.jpg'
        HERO_ZERO = 'change_hero/hero_zero.jpg'
        HERO_START = 'change_hero/hero_start.jpg'

    def getPathEnum(self):
        return ChangeHeroAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False
        self.step = 0
        self.heroNum = 0
        self.checkTagsCount = -1

    def start(self, heroNum):
        self.reset()
        self.step = 0
        self.runing = True
        self.heroNum = heroNum

    def stop(self):
        self.reset()
        self.runing = False

    def reset(self):
        self.step = 0
        self.heroNum = 0
        self.checkTagsCount = -1

    def actionChangeHero(self, image):
        if not self.runing:
            return False
        if self.heroNum <= 0 or self.heroNum > 10:
            print("heroNum必须为1-10")
            return
        if self.step == 0:
            resultSetting = self.match(image, ChangeHeroAction.Path.HERO_SETTING.value)
            if resultSetting:
                self.click(resultSetting)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 1
            time.sleep(0.3)
        elif self.step == 1:
            resultChange = self.match(image, ChangeHeroAction.Path.HERO_CHANGE.value)
            if resultChange:
                self.click(resultChange)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 2
            time.sleep(0.3)
        elif self.step == 2:
            resultTags = MatchHelper.match_templates(image, ChangeHeroAction.Path.HERO_TAG.value)
            resultZeros = MatchHelper.match_templates(image, ChangeHeroAction.Path.HERO_ZERO.value)
            matchResultMap = {ChangeHeroAction.Path.HERO_TAG.value: resultTags, ChangeHeroAction.Path.HERO_ZERO.value:resultZeros}
            self.updateMatchResultMap(matchResultMap)
            if resultTags:
                print("检测到英雄位置：",len(resultTags))
                # 容错：连续两次检测到相同数量才认为通过
                if self.checkTagsCount == len(resultTags):
                    resultTags = sorted(resultTags, key=lambda t: (t[1], t[0]))
                    if len(resultTags) >= self.heroNum:
                        print("选择英雄：",self.heroNum)
                        self.click(resultTags[self.heroNum-1])
                        time.sleep(random.uniform(0.8, 1.2))
                        self.step = 3
                    else:
                        print("异常，英雄检测失败")
                        self.stop()
                else:
                    self.checkTagsCount  = len(resultTags)
            time.sleep(0.5)
        elif self.step == 3:
            resultStart = self.match(image, ChangeHeroAction.Path.HERO_START.value)
            if resultStart:
                self.click(resultStart)
                time.sleep(random.uniform(0.8, 1.2))
                self.stop()

        return True
