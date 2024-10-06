
import component.utils.MatchHelper as MatchHelper
import random
import time
from component.action.BaseAction import BaseAction
from enum import Enum
import component.utils.RuntimeData as R
from component.action.ActionManager import actionManager
from component.utils.EventManager import eventManager


class ChangeHeroAction(BaseAction):

    class Path(Enum):
        HERO_SETTING = 'change_hero/hero_setting.jpg', (0.8, 1, 0, 0.33)
        HERO_CHANGE = 'change_hero/hero_change.jpg', (0.5, 0.8, 0.66, 1)
        HERO_TAG = 'change_hero/hero_tag.jpg', None
        HERO_ZERO = 'change_hero/hero_zero.jpg', None
        HERO_START = 'change_hero/hero_start.jpg', (0.33, 0.66, 0.66, 1)

        def __init__(self, path, area):
            self.path = path
            self.area = area

    def getPathEnum(self):
        return ChangeHeroAction.Path

    def __init__(self, ctrl, matchResultMap: dict):
        super().__init__(ctrl, matchResultMap)
        self.runing = False
        self.step = 0
        self.checkTagsCount = -1

    def start(self, step=0):
        self.reset()
        self.step = step
        self.runing = True

    def stop(self):
        self.reset()
        self.removeAllResults()
        self.runing = False

    def reset(self):
        self.step = 0
        self.checkTagsCount = -1

    def actionChangeHero(self, image):
        if not self.runing:
            return False
        if self.step == 0:
            resultSetting = self.match(image, ChangeHeroAction.Path.HERO_SETTING)
            if resultSetting:
                self.click(resultSetting)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 1
            time.sleep(0.3)
        elif self.step == 1:
            resultChange = self.match(image, ChangeHeroAction.Path.HERO_CHANGE)
            if resultChange:
                self.click(resultChange)
                time.sleep(random.uniform(0.8, 1.2))
                self.step = 2
            time.sleep(0.3)
        elif self.step == 2:
            resultTags = MatchHelper.match_templates(image, ChangeHeroAction.Path.HERO_TAG.path)
            resultZeros = MatchHelper.match_templates(image, ChangeHeroAction.Path.HERO_ZERO.path)
            matchResultMap = {ChangeHeroAction.Path.HERO_TAG.path: resultTags, ChangeHeroAction.Path.HERO_ZERO.path: resultZeros}
            self.updateMatchResultMap(matchResultMap)
            if resultTags:
                print("检测到英雄位置：", len(resultTags))
                # 容错：连续两次检测到相同数量才认为通过
                if self.checkTagsCount == len(resultTags):
                    resultTags = sorted(resultTags, key=lambda t: (t[1], t[0]))
                    # 更新英雄疲劳数据
                    self.__updateHeros(resultTags, resultZeros)
                    print(R.HEROS)
                    # 下一位
                    heroNum = self.__nextHero()
                    print("切换到下一位：", heroNum)
                    if heroNum:
                        # 选择英雄
                        if len(resultTags) >= heroNum:
                            print("选择英雄：", heroNum)
                            self.click(resultTags[heroNum-1])
                            time.sleep(random.uniform(0.8, 1.2))
                            R.CURRENT_HERO = heroNum
                            self.step = 3
                        else:
                            print("异常，英雄检测失败")
                            self.stop()
                    else:
                        print("设定的角色疲劳已全部耗尽,停止脚本。")
                        self.stop()
                        eventManager.publish('FINISH_EVENT')
                        return True
                else:
                    self.checkTagsCount = len(resultTags)
            time.sleep(0.5)
        elif self.step == 3:
            resultStart = self.match(image, ChangeHeroAction.Path.HERO_START)
            if resultStart:
                print("已选择英雄，点击开始")
                self.click(resultStart)
                time.sleep(random.uniform(3, 4))
                self.stop()
                # 切换英雄完成，检查页面活动广告
                actionManager.advertAction.start()

        return True

    # 更新英雄疲劳数据
    def __updateHeros(self, resultTags: list, resultZeros: list):
        def hasFinish(heroNum, width):
            endX = resultTags[heroNum-1][0]
            startX = endX - width
            if resultZeros is not None:
                for zero in resultZeros:
                    if zero[0] > startX and zero[0] < endX:
                        return True
            return False
        # 只有一个英雄的情况暂时不写
        if len(resultTags) >= 2:
            width = resultTags[1][0] - resultTags[0][0]
            for hero in R.HEROS:
                if hasFinish(hero, width):
                    R.HEROS[hero] = True

    def __nextHero(self):
        for hero, finish in R.HEROS.items():
            if not finish:
                return hero
        return None
