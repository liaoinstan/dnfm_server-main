import time
import math
from abc import abstractmethod
from component.adb.game_control import GameControl
from typing import List


class Hero:

    INSTANCE_MAP = {}

    @staticmethod
    def getInstance(heroJob: str, ctrl=None):
        if heroJob in Hero.INSTANCE_MAP:
            return Hero.INSTANCE_MAP[heroJob]
        else:
            if ctrl is None:
                return None
            print(f"初始化职业配置：{heroJob}{('(默认)'if heroJob == '奶妈' else '')}")
            if heroJob == "奶妈":
                from hero.naima import Naima
                hero = Naima(ctrl)
            elif heroJob == "鬼泣":
                from hero.guiqi import Guiqi
                hero = Guiqi(ctrl)
            elif heroJob == "剑魂":
                from hero.jianhun import Jianhun
                hero = Jianhun(ctrl)
            elif heroJob == "剑豪":
                from hero.jianhao import Jianhao
                hero = Jianhao(ctrl)
            elif heroJob == "暗帝":
                from hero.andi import Andi
                hero = Andi(ctrl)
            elif heroJob == "剑宗":
                from hero.jianzong import JianZong
                hero = JianZong(ctrl)
            else:
                hero = None
            if hero:
                Hero.INSTANCE_MAP[heroJob] = hero
                return hero
            else:
                print(f"职业配置错误，使用默认奶奶配置（职业【{heroJob}】不在hero.py的配置中,请优先处理此问题！）")
                from hero.naima import Naima
                return Naima(ctrl)

    def __init__(self, ctrl):
        self.ctrl: GameControl = ctrl
        self.pre_room_num = -1
        self.last_angle = 0
        self.last_auto_skill_time = 0
        import os
        import json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.dict = self.skillMap()
        
    def control(self, hero_pos, image, boxs, MapNumber):
        # 首次进入房间释放预定技能
        if self.pre_room_num != MapNumber:
            self.action(MapNumber)
            self.pre_room_num = MapNumber
            return 0
        else:
            self.pre_room_num = MapNumber
        # 预订技能释放后还有怪物，进行自动攻击
        return self.control_auto(hero_pos, boxs)

    @abstractmethod
    def skillMap(self) -> List[str]:
        pass
    
    @abstractmethod
    def action(self, roomNum):
        pass

    @abstractmethod
    def get_auto_skill(self) -> List[str]:
        pass

    def special_action(self, last_room_num, room_num):
        pass

    def skill(self, name, t=0, need_print=True, prefix="释放预定技能"):
        self.ctrl.skill(self.dict[name], t)
        if need_print:
            print(f"{prefix}:" + name)

    def calculate_center(self, box):  # 计算矩形框的底边中心点坐标
        return ((box[0] + box[2]) / 2, box[3])

    def calculate_distance(self, center1, center2):  # 计算两个底边中心点之间的欧几里得距离
        return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

    def find_closest_box(self, boxes, target_box):  # 计算目标框的中心点
        target_center = self.calculate_center(target_box)  # 初始化最小距离和最近的box
        min_distance = float('inf')
        closest_box = None  # 遍历所有box，找出最近的box
        for box in boxes:
            center = self.calculate_center(box)
            distance = self.calculate_distance(center, target_center)
            if distance < min_distance:
                min_distance = distance
                closest_box = box
        return closest_box, min_distance

    def find_close_point_to_box(self, boxes, point):
        target_center = point  # 初始化最小距离和最近的box
        min_distance = float('inf')
        closest_box = None  # 遍历所有box，找出最近的box
        for box in boxes:
            center = self.calculate_center(box)
            distance = self.calculate_distance(center, target_center)
            if distance < min_distance:
                min_distance = distance
                closest_box = box
        return closest_box, min_distance

    def calculate_point_to_box_angle(self, point, box):
        center1 = point
        center2 = self.calculate_center(box)
        delta_x = center2[0] - center1[0]  # 计算相对角度（以水平轴为基准）
        delta_y = center2[1] - center1[1]
        angle = math.atan2(delta_y, delta_x)
        angle_degrees = math.degrees(angle)  # 将角度转换为度数
        adjusted_angle = - angle_degrees
        return adjusted_angle

    def calculate_angle(self, box1, box2):  # 计算两个框的底边中心点
        center1 = self.calculate_center(box1)
        center2 = self.calculate_center(box2)
        delta_x = center2[0] - center1[0]  # 计算相对角度（以水平轴为基准）
        delta_y = center2[1] - center1[1]
        angle = math.atan2(delta_y, delta_x)
        angle_degrees = math.degrees(angle)  # 将角度转换为度数
        adjusted_angle = - angle_degrees
        return adjusted_angle

    def calculate_angle_to_box(self, box, x, y):  # 计算框到点的角度
        center = self.calculate_center(box)  # 计算矩形框的中心点
        angle = math.atan2(y - center[1], x - center[0])  # 计算从点 (x, y) 到中心点的角度
        angle_degrees = math.degrees(angle)  # 将角度转换为度数
        adjusted_angle = - angle_degrees
        return adjusted_angle

    def calculate_iou(self, box1, box2):
        # 计算相交区域的坐标
        inter_x_min = max(box1[0], box2[0])
        inter_y_min = max(box1[1], box2[1])
        inter_x_max = min(box1[2], box2[2])
        inter_y_max = min(box1[3], box2[3])
        # 计算相交区域的面积
        inter_area = max(0, inter_x_max - inter_x_min) * \
            max(0, inter_y_max - inter_y_min)
        # 计算每个矩形的面积和并集面积
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union_area = box1_area + box2_area - inter_area
        # 计算并返回IoU
        return inter_area / union_area if union_area > 0 else 0

    def normalize_angle(self, angle):  # 将角度规范化到 [-180, 180) 的范围内
        angle = angle % 360
        if angle >= 180:
            angle -= 360
        return angle

    def are_angles_on_same_side_of_y(self, angle1, angle2):  # 规范化角度
        norm_angle1 = self.normalize_angle(angle1)
        norm_angle2 = self.normalize_angle(angle2)  # 检查是否在 y 轴的同侧
        return (norm_angle1 >= 0 and norm_angle2 >= 0) or (norm_angle1 < 0 and norm_angle2 < 0)

    #######################################################################
    # 2024/9/15
    # 自动攻击执行逻辑
    #
    #######################################################################
    def control_auto(self, hero_pos, boxs):
        monster = boxs[boxs[:, 5] <= 2][:, :4]
        close_monster, distance = self.find_close_point_to_box(
            monster, hero_pos)
        close_monster_point = self.calculate_center(close_monster)
        angle = self.calculate_point_to_box_angle(hero_pos, close_monster)
        distance_x = abs(hero_pos[0]-close_monster_point[0])
        distance_y = abs(hero_pos[1]-close_monster_point[1])
        if not self.are_angles_on_same_side_of_y(self.last_angle, angle):
            self.ctrl.move(angle)
            self.ctrl.attack(False)
            time.sleep(0.1)
            self.ctrl.attack()
        elif distance_y < 0.1 and distance_x < 0.25:
            timeGap = int((time.time() - self.last_auto_skill_time) * 1000)
            if timeGap > 2500:
                skills = self.get_auto_skill()
                if skills is not None and len(skills) != 0:
                    for skill_name in skills:
                        self.skill(skill_name, need_print=False)
                        self.last_auto_skill_time = time.time()
                        time.sleep(0.5)
            else:
                self.ctrl.attack()
        else:
            distance = math.sqrt(distance_x**2 + distance_y**2)
            if distance > 0.3:
                self.ctrl.move(angle)
                self.ctrl.attack(False)
            else:
                self.ctrl.move(angle)
                self.ctrl.attack(False)
                time.sleep(distance*3)
                self.ctrl.attack(True)
        self.last_angle = angle
        return angle

    #################################################################################
    # 特殊动作
    # 默认特殊动作
    #################################################################################
    def special_action(self, last_room_num, room_num):
        if self.pre_room_num == room_num:
            return False
        if last_room_num == 5 and room_num == 6:
            self.ctrl.move(1)
            time.sleep(0.3)
            self.skill("后跳", prefix="特殊动作")
            time.sleep(0.1)
            self.skill("后跳", prefix="特殊动作")
            time.sleep(0.1)
            self.ctrl.move(1)
            time.sleep(0.3)
            self.skill("后跳", prefix="特殊动作")
            time.sleep(0.1)
            self.skill("后跳", prefix="特殊动作")
            time.sleep(0.1)
            self.pre_room_num = room_num
            return True
        else:
            return False
