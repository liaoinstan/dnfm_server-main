import time
import math


class Hero:
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.pre_room_num = -1
        self.last_angle = 0
        self.last_auto_skill_time = 0
        import os
        import json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "naima.json")
        with open(file_path, 'r', encoding='utf-8') as file:
            self.dict = json.load(file)  # 解析 JSON 文件

    def skill(self, name, t=0):
        self.ctrl.skill(self.dict[name], t)
        print("释放预定技能:" + name)

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
    def control_auto(self, hero_pos, boxs, call_get_skill):
        monster = boxs[boxs[:, 5] <= 2][:, :4]
        close_monster, distance = self.find_close_point_to_box(
            monster, hero_pos)
        close_monster_point = self.calculate_center(close_monster)
        angle = self.calculate_point_to_box_angle(hero_pos, close_monster)
        if not self.are_angles_on_same_side_of_y(self.last_angle, angle):
            self.ctrl.move(angle)
            self.ctrl.attack(False)
            time.sleep(0.1)
            self.ctrl.attack()
        elif abs(hero_pos[1]-close_monster_point[1]) < 0.1 and abs(hero_pos[0]-close_monster_point[0]) < 0.15:
            timeGap = int((time.time() - self.last_auto_skill_time) * 1000) 
            if timeGap > 2500:
                skills = call_get_skill()
                if skills is not None and len(skills) != 0:
                    for skill_name in skills[0]:
                        skill_name = skills[0]
                        self.skill(skill_name)
                        self.last_auto_skill_time = time.time()
                        time.sleep(0.5)
            else:
                self.ctrl.attack()
        else:
            self.ctrl.move(angle)
            self.ctrl.attack(False)
        self.last_angle = angle
        return angle
