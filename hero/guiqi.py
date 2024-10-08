import time
from .hero import Hero


class Guiqi(Hero):

    # 职业键位映射表
    def skillMap(self):
        return {
            "后跳": "Jump_Back",
            "爪子": "button1",
            "小炎剑": "button2",
            "鬼影剑": "button3",
            "月光闪": "button4",
            "墓碑": "button5",
            "地裂波动剑": "button6",
            "闪": "button7",
            "觉醒": "button8",
            "冥炎剑": "button9",
            "冰阵": "button10",
            "毒阵": "button11",
            "减防": "button12",
            "上增益": "button13",
            "temp3": "button14",
            "temp4": "button15"
        }

    # 预设每个房间的行为
    def action(self, MapNumber):
        wait = 0.1
        if MapNumber == 0:
            self.ctrl.reset()
            time.sleep(wait)
            self.skill("上增益")
            time.sleep(1.0)
            self.ctrl.move(330)
            time.sleep(0.4)
            self.ctrl.move(0)
            time.sleep(0.8)
            self.skill("鬼影剑")
            time.sleep(0.5)
            self.skill("地裂波动剑")
        elif MapNumber == 1:
            time.sleep(wait)
            self.ctrl.move(320)
            time.sleep(0.5)
            self.ctrl.move(0)
            time.sleep(0.05)
            self.skill("墓碑")
        elif MapNumber == 2:
            time.sleep(wait)
            self.ctrl.move(330)
            time.sleep(0.3)
            self.skill("爪子")
            self.ctrl.move(0)
            time.sleep(1)
            self.skill("小炎剑")
        elif MapNumber == 3:
            time.sleep(wait)
            self.ctrl.move(340)
            time.sleep(0.4)
            self.skill("毒阵")
            time.sleep(0.5)
            self.skill("减防")
        elif MapNumber == 4:
            time.sleep(wait)
            self.ctrl.move(145)
            time.sleep(0.65)
            self.ctrl.move(1)
            time.sleep(0.05)
            self.skill("闪")
            self.ctrl.move(180)
            time.sleep(0.1)
            self.skill("地裂波动剑")
        elif MapNumber == 5:
            time.sleep(wait)
            self.ctrl.move(200)
            time.sleep(0.7)
            self.ctrl.move(1)
            time.sleep(0.7)
            self.ctrl.move(180)
            time.sleep(0.05)
            self.skill("觉醒")
            time.sleep(0.4)
            self.skill("觉醒")
            time.sleep(0.4)
            self.skill("冰阵")
            time.sleep(0.4)
            self.skill("冰阵")
        elif MapNumber == 6:
            var = None
        elif MapNumber == 7:
            time.sleep(wait)
            self.ctrl.move(335)
            time.sleep(0.4)
            self.ctrl.move(1)
            time.sleep(0.2)
            self.skill("鬼影剑")
            time.sleep(1)
            self.skill("毒阵")
        elif MapNumber == 8:
            time.sleep(wait)
            self.ctrl.move(340)
            time.sleep(0.6)
            self.ctrl.move(1)
            time.sleep(0.1)
            self.skill("墓碑")
        elif MapNumber == 9:
            time.sleep(wait)
            self.ctrl.move(350)
            time.sleep(0.6)
            self.ctrl.move(0)
            self.skill("冥炎剑")
            time.sleep(0.7)
            self.skill("地裂波动剑")
            time.sleep(0.8)
            self.skill("冰阵")

    #################################################################################
    # 2024/9/15
    # 自动攻击执行逻辑
    # 给角色安排1-2个冷却低的小技能（最好是不在上面的预定施放列表中的）
    # 自动攻击期间，每隔2.5秒，尝试施放一次该技能，其余时间普攻
    # （把几个小技能做成一键连招可以节省键位，只需填写连招第一个技能名，每2.5秒会点一次连招）
    #
    #################################################################################
    def get_auto_skill(self):
        return ["月光闪"]
