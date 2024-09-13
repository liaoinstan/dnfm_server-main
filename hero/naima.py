import time
import math
from .hero import Hero

#通用逻辑已迁移至父类Hero,其他英雄请继承Hero
class Naima(Hero):
    def __init__(self, ctrl):
        super().__init__(ctrl)

    def control(self, hero_pos, image, boxs, MapNumber):
        if self.pre_room_num != MapNumber:
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
                self.skill("审判锤击")
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
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(5)
                self.skill("惩戒加身")
                time.sleep(0.4)
                self.ctrl.move(180)
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
                self.skill("审判锤击")
                time.sleep(2)
                self.skill("勇气颂歌")
            elif MapNumber == 10:
                MapNumber == 9
            self.pre_room_num = MapNumber
            return 0
        self.pre_room_num = MapNumber
        monster = boxs[boxs[:, 5] <= 2][:, :4]
        close_monster, distance = self.find_close_point_to_box(monster, hero_pos)
        close_monster_point = self.calculate_center(close_monster)
        angle = self.calculate_point_to_box_angle(hero_pos, close_monster)
        if not self.are_angles_on_same_side_of_y(self.last_angle, angle):
            self.ctrl.move(angle)
            self.ctrl.attack(False)
        elif abs(hero_pos[1]-close_monster_point[1]) < 0.1 and abs(hero_pos[0]-close_monster_point[0]) < 0.15:
            self.ctrl.attack()
        else:
            self.ctrl.move(angle)
            self.ctrl.attack(False)
        self.last_angle = angle
        return angle
