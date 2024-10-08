import time
from .hero import Hero


class JianZong(Hero):

    # 职业键位映射表
    def skillMap(self):
        return {
            "后跳": "Jump_Back",
            "跳跃": "Jump",
            "疾影斩": "button1",
            "魔剑奥义": "button2",
            "瞬影三绝斩": "button3",
            "呼啦圈": "button4",
            "恶即斩": "button5",
            "穿云破空剑": "button6",
            "升龙剑": "button7",
            "抓取": "button8",
            "觉醒": "button9",
            "上属性Buff": "button10",
            "temp4": "button11",
            "temp3": "button12",
            "上Buff": "button13",
            "连环斩": "button14",
            "雷鸣千军破": "button15"
        }

    # 预设每个房间的行为
    def action(self, MapNumber):
        wait = 0.1
        if MapNumber == 0:
            self.ctrl.reset()
            time.sleep(wait)
            self.skill("上Buff")
            time.sleep(1.2)
            self.ctrl.move(330)
            time.sleep(0.4)
            self.ctrl.move(0)
            time.sleep(0.8)
            self.skill("恶即斩", 0.7)
            time.sleep(1.2)
        elif MapNumber == 1:
            time.sleep(wait)
            self.ctrl.move(220)
            time.sleep(0.55)
            self.ctrl.move(350)
            time.sleep(0.3)
            self.ctrl.move(0)
            self.skill("雷鸣千军破")
            time.sleep(1.2)
        elif MapNumber == 2:
            time.sleep(wait)
            time.sleep(2.0)
            # self.skill("幻剑术")
            # time.sleep(1)
            self.skill("升龙剑")
        elif MapNumber == 3:
            time.sleep(wait)
            self.ctrl.move(320)
            time.sleep(0.1)
            self.skill("呼啦圈", 0.5)
            time.sleep(0.5)
        elif MapNumber == 4:
            time.sleep(wait)
            self.ctrl.move(140)
            time.sleep(0.8)
            self.ctrl.move(1)
            time.sleep(0.05)
            self.skill("瞬影三绝斩")
            time.sleep(0.5)
        elif MapNumber == 5:
            time.sleep(wait)
            self.ctrl.move(180)
            time.sleep(0.4)
            self.skill("觉醒")
            time.sleep(0.4)
            self.skill("觉醒")
            time.sleep(0.4)
            self.skill("觉醒")
            time.sleep(0.4)
            self.skill("觉醒")
        elif MapNumber == 6:
            var = None
        elif MapNumber == 7:
            time.sleep(wait)
            self.ctrl.move(335)
            time.sleep(0.5)
            self.skill("雷鸣千军破")
            time.sleep(1.2)
        elif MapNumber == 8:
            time.sleep(wait)
            self.ctrl.move(340)
            time.sleep(0.2)
            self.ctrl.move(0)
            time.sleep(0.1)
            self.skill("呼啦圈", 1)
            time.sleep(0.5)
        elif MapNumber == 9:
            time.sleep(wait)
            self.ctrl.move(340)
            time.sleep(0.5)
            self.ctrl.move(0)
            self.skill("恶即斩", 0.7)
            time.sleep(2.0)
            self.skill("瞬影三绝斩")
            time.sleep(0.5)

    #################################################################################
    # 2024/9/15
    # 自动攻击执行逻辑
    # 给角色安排1-2个冷却低的小技能（最好是不在上面的预定施放列表中的）
    # 自动攻击期间，每隔2.5秒，尝试施放一次该技能，其余时间普攻
    # （把几个小技能做成一键连招可以节省键位，只需填写连招第一个技能名，每2.5秒会点一次连招）
    #
    #################################################################################
    def get_auto_skill(self):
        return ["疾影斩"]
