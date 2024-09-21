from game_control import GameControl
import time
import cv2
import math
import numpy as np
from enum import Enum
from collections import deque
import threading
from adbutils import adb
from utils.BWJRoomHelperV2 import Direction, roomHelper
from action.GoToWorkAction import GoToWorkAction
from action.FixAction import FixAction
from action.ChangeHeroAction import ChangeHeroAction
import random
import utils.MatchHelper as MatchHelper
from config import AGAIN,GOHOME,REPAIR_TIMES



def calculate_center(box):# 计算矩形框的底边中心点坐标
    return ((box[0] + box[2]) / 2, box[3])
def calculate_distance(center1, center2):# 计算两个底边中心点之间的欧几里得距离
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)
def find_closest_box(boxes, target_box):# 计算目标框的中心点
    target_center = calculate_center(target_box)# 初始化最小距离和最近的box
    min_distance = float('inf')
    closest_box = None# 遍历所有box，找出最近的box
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center) 
        if distance < min_distance:
            min_distance = distance
            closest_box = box
    return closest_box,min_distance
def find_farthest_box(boxes, target_box):
    target_center = calculate_center(target_box)# 计算目标框的中心点
    max_distance = -float('inf')# 初始化最大距离和最远的box
    farthest_box = None
    for box in boxes:# 遍历所有box，找出最远的box
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance > max_distance:
            max_distance = distance
            farthest_box = box
    return farthest_box, max_distance
def find_closest_or_second_closest_box(boxes, point):
    """找到离目标框最近的框或第二近的框"""
    if len(boxes) < 2:
        # 如果框的数量少于两个，直接返回最近的框
        target_center = point
        closest_box = None
        min_distance = float('inf')
        for box in boxes:
            center = calculate_center(box)
            distance = calculate_distance(center, target_center)
            if distance < min_distance:
                min_distance = distance
                closest_box = box
        return closest_box,distance
    # 如果框的数量不少于两个
    target_center = point
    # 初始化最小距离和最近的框
    min_distance_1 = float('inf')
    closest_box_1 = None
    # 初始化第二近的框
    min_distance_2 = float('inf')
    closest_box_2 = None
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance < min_distance_1:
            # 更新第二近的框
            min_distance_2 = min_distance_1
            closest_box_2 = closest_box_1
            # 更新最近的框
            min_distance_1 = distance
            closest_box_1 = box
        elif distance < min_distance_2:
            # 更新第二近的框
            min_distance_2 = distance
            closest_box_2 = box
    # 返回第二近的框
    return closest_box_2,min_distance_2
def find_close_point_to_box(boxes, point):#找距离点最近的框
    target_center = point# 初始化最小距离和最近的box
    min_distance = float('inf')
    closest_box = None# 遍历所有box，找出最近的box
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center) 
        if distance < min_distance:
            min_distance = distance
            closest_box = box
    return closest_box,min_distance
def calculate_point_to_box_angle(point, box):#计算点到框的角度
    center1 = point
    center2 = calculate_center(box)
    delta_x = center2[0] - center1[0]# 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle
def calculate_angle(box1, box2): 
    center1 = calculate_center(box1)
    center2 = calculate_center(box2)
    delta_x = center2[0] - center1[0]# 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle
def calculate_gate_angle(point, gate): 
    center1 = point
    center2 = ((gate[0]+gate[2])/2,(gate[3]-gate[1])*0.65+gate[1]) #计算门的重合点，水平方向取x轴中心，y轴方法为上65%下35%位置
    delta_x = center2[0] - center1[0]# 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle

def calculate_angle_to_box(point1,point2):#计算点到点的角度
    angle = math.atan2(point2[1] -point1[1], point2[0] - point1[0])# 计算从点 (x, y) 到中心点的角度
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle
def calculate_iou(box1, box2):
    # 计算相交区域的坐标
    inter_x_min = max(box1[0], box2[0])
    inter_y_min = max(box1[1], box2[1])
    inter_x_max = min(box1[2], box2[2])
    inter_y_max = min(box1[3], box2[3])
    # 计算相交区域的面积
    inter_area = max(0, inter_x_max - inter_x_min) * max(0, inter_y_max - inter_y_min)
    # 计算每个矩形的面积和并集面积
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    # 计算并返回IoU
    return inter_area / union_area if union_area > 0 else 0
def normalize_angle(angle):# 将角度规范化到 [-180, 180) 的范围内
    angle = angle % 360
    if angle >= 180:
        angle -= 360
    return angle
def are_angles_on_same_side_of_y(angle1, angle2):# 规范化角度
    norm_angle1 = normalize_angle(angle1)
    norm_angle2 = normalize_angle(angle2)# 检查是否在 y 轴的同侧
    return (norm_angle1 >= 0 and norm_angle2 >= 0) or (norm_angle1 < 0 and norm_angle2 < 0)
def is_image_almost_black(image, threshold=30):# 读取图片
    image = cv2.cvtColor(image, cv2.IMREAD_GRAYSCALE)# 检查图片是否成功读取
    num_black_pixels = np.sum(image < threshold)
    total_pixels = image.size
    black_pixel_ratio = num_black_pixels / total_pixels# 定义一个比例阈值来判断图片是否接近黑色
    return black_pixel_ratio > 0.7        
names =['Monster', #0
        'Monster_ds', #1
        'Monster_szt', #2
        'card', #3
        'equipment',#4 
        'go', #5
        'hero', #6
        'map', #7
        'opendoor_d', #8
        'opendoor_l', #9
        'opendoor_r', #10
        'opendoor_u', #11
        'pet',# 12
        'diamond']# 13
class ActionStatus(Enum):
    NONE = 0
    AGAIN = 1
    GOHOME = 2
from hero.naima import Naima
from hero.guiqi import Guiqi
from hero.jianhun import Jianhun
class GameAction:
    def __init__(self, ctrl: GameControl,queue):
        self.checkHero = "剑魂"
        # ---------- 英雄配置：
        if self.checkHero == "奶妈":
            self.control_attack = Naima(ctrl)
        if self.checkHero == "鬼泣":
            self.control_attack = Guiqi(ctrl)
        if self.checkHero == "剑魂":
            self.control_attack = Jianhun(ctrl)
        self.queue = queue
        self.ctrl = ctrl
        self.againRetryCount = 0
        self.actionStatus = ActionStatus.NONE
        self.pre_state = True #是否过图中
        self.stop_event = True
        self.reset_event = False
        self.room_num = -1
        self.last_room_num = -1
        self.hasKillSZT = False
        self.timeOut = 0
        self.againTimeOut = 0
        self.buwanjia = [8,10,10,11,9,10,10,10,10,10,8,8]
        self.thread_run = True
        self.thread = threading.Thread(target=self.control)  # 创建线程，并指定目标函数
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.thread.start()
        self.count = 1
        self.isFinish = False
        self.matchResultMap = {}
        self.goToWorkAction = GoToWorkAction(self.ctrl, self.matchResultMap)
        self.fixAction = FixAction(self.ctrl, self.matchResultMap)
        self.changeHeroAction = ChangeHeroAction(self.ctrl, self.matchResultMap)
    def quit(self):
        self.thread_run = True
    def reset(self):
        self.thread_run = False
        time.sleep(0.1)
        self.hasKillSZT = False
        self.room_num = -1
        self.last_room_num = -1
        self.actionStatus = ActionStatus.NONE
        self.pre_state = True
        self.thread_run = True
        self.thread = threading.Thread(target=self.control)  # 创建线程，并指定目标函数
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.timeOut = 0
        self.goToWorkAction.stop()
        self.fixAction.stop()
        self.changeHeroAction.stop()
        self.thread.start()
    def convertDirection(self, dNum:int):
        if dNum == 8:
            return Direction.BOTTOM
        elif dNum == 9:
            return Direction.LEFT
        elif dNum == 10:
            return Direction.RIGHT
        elif dNum == 11:
            return Direction.TOP
    def control(self):
        last_room_pos = []
        hero_track = deque()
        hero_track.appendleft([0,0])
        last_angle = 0
        while self.thread_run:
            if self.stop_event:
                time.sleep(0.001)
                self.count = 1
                self.ctrl.reset()
                self.matchResultMap.clear()
                continue
            if self.queue.empty():
                time.sleep(0.001)
                continue
            image,boxs = self.queue.get()
            
            if self.goToWorkAction.actionWayToBWJ(image):
                continue
            if self.fixAction.actionFix(image):
                continue
            if self.changeHeroAction.actionChangeHero(image):
                continue
            
            # 检测是否通关
            card = boxs[boxs[:,5]==3][:,:4]
            if len(card)>=8:
                time.sleep(1)
                self.ctrl.click(0.25*image.shape[0],0.25*image.shape[1])
                self.actionStatus = ActionStatus.AGAIN
                self.isFinish = True
                print("已检测到卡牌")
                # 每5把修一次装备，首次也会维修
                if self.count % REPAIR_TIMES == 1:
                    self.fixAction.start()
                time.sleep(3)
                
            # 检测是否重开
            if self.isFinish:
                resultLoading = MatchHelper.match_template(image, "way_to_bwj/loading.jpg")
                if resultLoading:
                    self.count += 1
                    print(f"\n==================第{self.count}轮==================")
                    self.actionStatus = ActionStatus.NONE
                    self.againTimeOut = 0
                    self.isFinish = False
                    self.room_num = 0
                    self.last_room_num = 0
                    self.hasKillSZT = False
                    self.timeOut = 0
                    hero_track = deque()
                    hero_track.appendleft([0,0])
                
            # 检测当前房间
            room_num = roomHelper.parseRoomNum(image)
            if room_num == 5:
                #去过5号房就表示击杀了狮子头
                self.hasKillSZT = True
            # 杀了狮子头后把房间号重排，以兼容以前的过图逻辑
            # 以前的逻辑因为4号房会经过两次，击杀狮子头出来后4号被重新编为6号房，之后的6,7,8分别为7,8,9
            if self.hasKillSZT and room_num == 4:
                room_num = 6
            else:
                if room_num == 6:
                    room_num = 7
                elif room_num == 7:
                    room_num = 8
                elif room_num == 8:
                    room_num = 9
                elif room_num == 9:
                    room_num = 10
                elif room_num == 10:
                    room_num = 11
            if self.isFinish:
                # 已通关，不再检测房间
                room_num = 9
                
            # 检测行动方向
            if room_num>=0:
                direction = self.buwanjia[room_num]
                if not self.hasKillSZT and (room_num == 7 or room_num == 8):
                    # 如果还没打狮子头就意外进了7号房，那么向左边走
                    direction = 9
                roomHelper.direction = self.convertDirection(direction)
            
            # 过滤黑屏
            if room_num == -1 or room_num == -2:
                if self.room_num != -1 and self.room_num != -2:
                    self.last_room_num = self.room_num
                    self.room_num = room_num
                    print("过图")
                    last_room_pos = hero_track[0]
                    hero_track = deque()
                    hero_track.appendleft([1-last_room_pos[0],1-last_room_pos[1]])
                    last_angle = 0
                    self.ctrl.reset()
                    self.timeOut = 0
                    time.sleep(0.5)
                continue
            
            hero = boxs[boxs[:,5]==6][:,:5]
            if self.room_num != room_num :
                if (self.room_num>=0):
                    print(f"\n【房间识别异常】 纠正当前房间号：{self.room_num} -> {room_num}")
                self.room_num = room_num
                if len(hero) > 0:
                    self.pre_state = False
                    print("房间号：",f"{self.last_room_num} -> {self.room_num}(当前)")
                    print("目标",self.directionOfDoorNum(direction))
                else:
                    print("异常：没检测到英雄")
                    continue
                
            gate = boxs[boxs[:,5]==direction][:,:4]
            arrow = boxs[boxs[:, 5] == 5][:,:4]
            equipment = [[detection[0], detection[1] + (detection[3] - detection[1]), detection[2], detection[3] + (detection[3] - detection[1]), detection[4], detection[5]]
                        for detection in boxs if detection[5] == 4 and detection[4] > 0.3]
            monster = boxs[boxs[:,5]<=2][:,:4]
            diamond = boxs[boxs[:,5]==13][:,:4]
            angle = 0
            outprint = ''
            self.calculate_hero_pos(hero_track,hero)#计算英雄位置
            if self.againTimeOut != 0:
                waitAgainTime = int((time.time() - self.againTimeOut) * 1000) 
                if waitAgainTime > 7000:
                    self.actionStatus = ActionStatus.GOHOME
            # 计算操作是否超时(已经结束关卡，或等待再次挑战期间不计时)
            if self.timeOut == 0 or self.isFinish or self.againTimeOut != 0:
                waitTime = 0
            else:
                waitTime = int((time.time() - self.timeOut) * 1000) 
            if self.control_attack.special_action(self.last_room_num, self.room_num):
                print('执行特殊动作')
                continue
            # 超时补救措施
            if waitTime > 5000:
                outprint = '卡位补救措施'
                random_angle = random.randint(0, 360)
                print('\n检测到卡位,尝试脱离卡位,角度:',random_angle, end='\n')
                self.ctrl.attack(False) 
                self.ctrl.move(random_angle)
                time.sleep(1)
                self.timeOut = 0
            elif len(monster)>0:
                outprint = '有怪物'
                angle = self.control_attack.control(hero_track[0],image,boxs,self.room_num)
                self.timeOut = 0
            elif len(equipment)>0:
                outprint = '有材料'
                if len(gate)>0:
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    farthest_item,distance = find_farthest_box(equipment,close_gate)
                    angle = calculate_point_to_box_angle(hero_track[0],farthest_item)
                else:
                    close_item,distance = find_close_point_to_box(equipment,hero_track[0])
                    angle = calculate_point_to_box_angle(hero_track[0],close_item)
                self.ctrl.attack(False)
                self.ctrl.move(angle)
                self.timeOut = 0
            elif len(gate)>0:
                outprint = '有门'
                if direction == 9:#左门
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    angle = calculate_gate_angle(hero_track[0],close_gate)
                    self.ctrl.attack(False)
                    self.ctrl.move(angle)
                else:
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    angle = calculate_point_to_box_angle(hero_track[0],close_gate)
                    self.ctrl.attack(False)
                    self.ctrl.move(angle)
                if self.timeOut == 0:
                    self.timeOut = time.time()
            elif len(arrow)>0 and self.room_num != 4:
                outprint = '有箭头'
                close_arrow,distance = find_closest_or_second_closest_box(arrow,hero_track[0])
                angle = calculate_point_to_box_angle(hero_track[0],close_arrow)
                self.ctrl.move(angle)
                self.ctrl.attack(False)
                if self.timeOut == 0:
                    self.timeOut = time.time()
            elif self.actionStatus == ActionStatus.AGAIN:
                print("\n检测再次挑战")
                self.ctrl.move(0)
                time.sleep(2)
                # 获取连接的设备列表
                adb.device().click(*AGAIN)
                if self.againTimeOut ==0:
                    self.againTimeOut = time.time()
                # self.actionStatus = ActionStatus.NONE
            elif self.actionStatus == ActionStatus.GOHOME:
                print("\n返回城镇")
                self.ctrl.move(0)
                self.againTimeOut = 0
                time.sleep(1)
                adb.device().click(*GOHOME)
                time.sleep(1)
                adb.device().click(*GOHOME)
                self.room_num = 0
                self.last_room_num = 0
                self.actionStatus = ActionStatus.NONE
            else :
                outprint = "无目标"
                if self.room_num == 4:
                    angle = calculate_angle_to_box(hero_track[0],[0.25,0.6])
                else:
                    angle = calculate_angle_to_box(hero_track[0],[0.5,0.75])
                self.ctrl.move(angle)
                self.ctrl.attack(False) 
            waitStr = waitTime = f"{waitTime} ms" if waitTime <=5000 else "超时"
            if time == 0:
                print("\r", end='')
                print(f"\r当前进度:{outprint},角度{int(angle):04d}，位置{hero_track[0]}", end="")
            else:
                print("\r", end='')
                print(f"\r当前进度:{outprint},角度{int(angle):04d}，位置{hero_track[0]}，行动时间:{waitStr} ", end="")
    def calculate_hero_pos(self,hero_track,boxs):
        if len(boxs)==0:
            None
        elif len(boxs)==1:
            hero_track.appendleft(calculate_center(boxs[0]))
        elif len(boxs)>1:
            # 以前的逻辑是使用距离上一次位置<10%的英雄
            # for box in boxs:
            #     if calculate_distance(box,hero_track[0])<0.1:
            #         hero_track.appendleft(box)
            #         return
            #     hero_track.appendleft(hero_track[0])
            # 页面检查到多个英雄时，使用置信度最高的英雄
            maxThink = 0
            maxBox = None
            for box in boxs:
                if box[4] > maxThink:
                    maxThink = box[4]
                    maxBox = box
            hero_track.appendleft(calculate_center(maxBox))
                
                
    def directionOfDoorNum(self, doorNum):
        if doorNum == 8:
            return "向下"
        elif doorNum == 9:
            return "向左"
        elif doorNum == 10:
            return "向右"
        elif doorNum == 11:
            return "向上"