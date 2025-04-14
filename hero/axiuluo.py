import time
import math
from hero.hero import Hero


class Axiuluo(Hero):

    # 职业键位映射表
    def skillMap(self):
        return {
            "后跳": "Jump_Back",
            "杀意波动": "button1",
            "大冰": "button2",
            "邪光斩": "button3",
            "无双波": "button4",
            "修罗邪光阵": "button5",
            "大火": "button6",
            "怒气爆发": "button7",
            "觉醒": "button8",
            "": "button9",
            "": "button10",
            "": "button11",
            "temp1": "button12",
            "杀意波动": "button13",
            "temp2": "button14",
            "temp3": "button15"
        }

    def control(self, hero_pos, image, boxs, MapNumber):
        wait = 0.1
        if MapNumber == 0:
            self.ctrl.reset()
            time.sleep(wait)
            self.skill("杀意波动")
            time.sleep(1.2)
            self.ctrl.move(330)
            time.sleep(0.4)
            self.ctrl.move(0)
            time.sleep(0.4)
            self.skill("大冰")
            time.sleep(0.2)
            self.skill("邪光斩")
            time.sleep(0.1)
            self.skill("邪光斩")
            time.sleep(0.2)
            self.skill("邪光斩")
        elif MapNumber == 1:
            time.sleep(wait)
            self.ctrl.move(320)
            time.sleep(0.5)
            self.skill("无双波")
            time.sleep(0.5)
            self.skill("无双波")
        elif MapNumber == 2:
            time.sleep(wait)
            self.ctrl.move(310)
            time.sleep(0.3)
            self.skill("邪光斩", 0.4)
        elif MapNumber == 3:
            time.sleep(wait)
            self.ctrl.move(340)
            time.sleep(0.3)
            self.skill("修罗邪光阵")
            time.sleep(1.0)
            self.skill("觉醒")
        elif MapNumber == 4:
            time.sleep(wait)
            self.ctrl.move(20)
            time.sleep(0.9)
            self.ctrl.move(180)
            time.sleep(0.05)
            self.skill("大火")
            time.sleep(0.2)
            self.skill("邪光斩")
            time.sleep(0.1)
            self.skill("邪光斩")
            time.sleep(0.5)
            # self.skill("觉醒")
        elif MapNumber == 5:
            time.sleep(wait)
            time.sleep(0.1)
            self.skill("觉醒")
            self.ctrl.move(200)
            time.sleep(1.0)
            self.skill("不动明王阵")
            time.sleep(0.4)
            self.skill("不动明王阵")
            time.sleep(0.4)
            self.skill("不动明王阵")
            time.sleep(0.4)
            self.skill("不动明王阵")
        elif MapNumber == 6:
            var = None
        elif MapNumber == 7:
            time.sleep(wait)
            self.ctrl.move(335)
            time.sleep(0.4)
            self.ctrl.move(1)
            time.sleep(0.1)
            self.skill("大冰")
            time.sleep(0.2)
            self.skill("邪光斩")
            time.sleep(0.1)
            self.skill("邪光斩")
        elif MapNumber == 8:
            time.sleep(wait)
            time.sleep(0.7)
            self.skill("大火")
            time.sleep(0.5)
        elif MapNumber == 9:
            time.sleep(wait)
            self.ctrl.move(330)
            time.sleep(0.4)
            self.ctrl.move(0)
            self.skill("无双波")
            time.sleep(0.7)
            self.skill("无双波")
            time.sleep(1.0)
            self.skill("怒气爆发")

    #################################################################################
    # 2024/9/15
    # 自动攻击执行逻辑
    # 给角色安排1-2个冷却低的小技能（最好是不在上面的预定施放列表中的）
    # 自动攻击期间，每隔2.5秒，尝试施放一次该技能，其余时间普攻
    # （把几个小技能做成一键连招可以节省键位，只需填写连招第一个技能名，每2.5秒会点一次连招）
    #
    #################################################################################
    def get_auto_skill(self):
        return ["唤雷符"]
