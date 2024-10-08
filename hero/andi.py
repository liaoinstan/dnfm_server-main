import time
from .hero import Hero

# 通用逻辑已迁移至父类Hero,其他英雄请继承Hero


class Andi(Hero):

    # 职业键位映射表
    def skillMap(self):
        return {
            "后跳": "Jump_Back",
            "光明惩戒": "button1",
            "惩戒加身": "button2",
            "唤雷符": "button3",
            "沐天之光": "button4",
            "领悟之雷": "button5",
            "光芒烬盾": "button6",
            "胜利之矛": "button7",
            "觉醒": "button8",
            "光明之杖": "button9",
            "光明锁环": "button10",
            "勇气颂歌": "button11",
            "temp1": "button12",
            "勇气祝福": "button13",
            "temp2": "button14",
            "temp3": "button15"
        }

    # 预设每个房间的行为
    def action(self, MapNumber):
        wait = 0.1
        if MapNumber == 0:
            self.ctrl.reset()
            time.sleep(wait)
            self.skill("勇气祝福")
            time.sleep(1.2)
            self.ctrl.move(335)
            time.sleep(0.3)
            self.skill("光芒烬盾")
            time.sleep(0.5)
        elif MapNumber == 1:
            time.sleep(wait)
            self.ctrl.move(295)
            time.sleep(0.5)
            self.skill("光明之杖")
            time.sleep(1.5)
            self.skill("胜利之矛")
            time.sleep(0.5)
            self.skill("胜利之矛")
        elif MapNumber == 2:
            time.sleep(wait)
            time.sleep(0.5)
            self.skill("光明惩戒")
            time.sleep(1)
            self.skill("光芒烬盾")
            time.sleep(1)
            self.ctrl.move(360)
            self.skill("惩戒加身")
            time.sleep(1)
        elif MapNumber == 3:
            time.sleep(wait)
            self.ctrl.move(345)
            time.sleep(0.5)
            self.skill("勇气颂歌")
        elif MapNumber == 4:
            time.sleep(wait)
            self.ctrl.move(145)
            time.sleep(0.65)
            self.ctrl.move(1)
            time.sleep(0.05)
            self.skill("胜利之矛")
            time.sleep(0.5)
            self.ctrl.move(1)
            time.sleep(0.2)
            self.skill("光芒烬盾")
            time.sleep(0.8)
            self.skill("光明惩戒")
            time.sleep(0.5)
            self.skill("胜利之矛")
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
            self.skill("觉醒")
            time.sleep(0.4)
            self.skill("觉醒")
        elif MapNumber == 6:
            None
        elif MapNumber == 7:
            time.sleep(wait)
            self.ctrl.move(335)
            time.sleep(0.4)
            self.ctrl.move(0)
            self.skill("光芒烬盾")
            time.sleep(1.5)
            self.skill("沐天之光")
        elif MapNumber == 8:
            time.sleep(wait)
            self.ctrl.move(340)
            time.sleep(0.4)
            self.skill("胜利之矛")
            time.sleep(0.5)
            self.ctrl.move(1)
            time.sleep(1.5)
            self.skill("光明惩戒")
        elif MapNumber == 9:
            time.sleep(wait)
            print("当前BS房")
            self.ctrl.move(330)
            time.sleep(0.4)
            self.ctrl.move(0)
            self.skill("光明之杖")
            time.sleep(2)
            self.skill("勇气颂歌")

    #################################################################################
    # 2024/9/15
    # 自动攻击执行逻辑
    # 给角色安排1-2个冷却低的小技能（最好是不在上面的预定施放列表中的）
    # 自动攻击期间，每隔2.5秒，尝试施放一次该技能，其余时间普攻
    # （把几个小技能做成一键连招可以节省键位，只需填写连招第一个技能名，每2.5秒会点一次连招）
    #
    #################################################################################
    def get_auto_skill(self):
        return ["光明惩戒"]
