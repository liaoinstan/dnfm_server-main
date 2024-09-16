import PIL
import math
import cv2
import numpy as np
from collections import OrderedDict,deque
from PIL import Image, ImageDraw
from enum import Enum
from config import CENTER_POINT, OFFSET_ROOM

########################################################
#   只能在布万加副本内使用，目前只支持走布万加下路
#   以下参数需要根据自己设备进行调整
#   屏幕坐标可以在开发者选项中打开"指针位置"获取屏幕坐标
#   核心业务逻辑在parseRoomNum方法中，其余均为私有工具方法
#
#   如果出现识别不准确的情况，请仔细检查参数配置是否正确
#
# 小地图中心点坐标（蓝色小人）
# CENTER_POINT = (2954, 174)
# 小地图中心点距相邻房间中心点距离（=房间直径）
# OFFSET_ROOM = 77
# 小地图中心点距地图绿色小箭头中心点距离
# OFFSET_ARROW = 53
# 游戏窗口宽度（画布宽） / 设备屏幕真实宽度(屏幕分辨率)
# RATE = 800 / 3200
#
########################################################


class Direction(Enum):
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT_TOP = 4
    LEFT_BOTTOM = 5
    RIGHT_TOP = 6
    RIGHT_BOTTOM = 7


class BWJRoomHelper(object):
    def __init__(self):
        self.center: tuple
        self.offsetRoom: int
        self.offsetArrow: int
        self.img = None
        # 已走过的道路的颜色，用于区分小地图的房间是否已经清理
        self.wayColor = (211, 183, 128)
        # 小地图箭头颜色，用于识别小地图箭头朝向
        self.arrowColor = (99, 250, 14)
        # Buff图标颜色
        self.buffColor = (9, 154, 55)
        # 精英怪图标颜色
        self.mosterColor = (84, 56, 245)
        # 缓存，节省算力避免重复查找
        self.searchCache = {}
        # 是否开启区域查找（不开启只会查找指定的点，开启会查找以该点为中心11*11像素内的区域）
        self.searchByArea = True
        self.rate = 1
        self.cleanedRoom = OrderedDict()
        self.direction:Direction = None
        self.currentRoom = -2

    # 设备物理坐标转画布坐标
    def convet(self, x):
        return int(x*self.rate)

    # 使用前先初始化
    # rate：画布宽/屏幕宽，没设置画布默认1
    def init(self, rate=1):
        self.rate = rate
        self.center = (self.convet(
            CENTER_POINT[0]), self.convet(CENTER_POINT[1]))
        self.offsetRoom = self.convet(OFFSET_ROOM)
        self.offsetArrow = int(self.offsetRoom * 0.64)

    # 计算两个RGB颜色之间的欧氏距离，距离代表相似度，越小越相似
    def __euclideanColorDistance(self, color1, color2):
        return math.sqrt((color1[0] - color2[0])**2 + (color1[1] - color2[1])**2 + (color1[2] - color2[2])**2)

    # 判断两个RGB颜色是否大致相等，threshold越小相似度越高
    def __areColorsSimilar(self, color1, color2, threshold=30):
        distance = self.__euclideanColorDistance(color1, color2)
        return distance < threshold

    def __getColor(self, x, y):
        # 横屏模式下图片为(h,w,3)先取Y轴再取X轴
        return self.__BGR2RGB(self.img[y, x])

    def __hasColor(self, color, x, y):
        if self.searchByArea:
            # 先尝试从缓存中找是否先前已经查找过该点的颜色
            if (x, y) in self.searchCache:
                if self.__areColorsSimilar(color, self.searchCache[(x, y)]):
                    log("缓存中已找到:", color, x, y)
                    return True
                else:
                    # 如果缓存中有记录，且不是当前要查找的颜色，也不用查询了，返回False
                    log("缓存中没有找到:", color, x, y)
                    return False

            # 缓存中没有，则开始查找
            findColor = self.__findColorFormArea(color, x, y)
            log("区域查找已找到:", findColor, x, y)

            # 如果查找到指定颜色，将坐标和颜色值写入缓存
            if findColor:
                self.searchCache[(x, y)] = findColor
                return True
            else:
                return False
        else:
            # 只查找指定像素点
            return self.__areColorsSimilar(self.__getColor(x, y), color)

    def __BGR2RGB(self, color):
        return (color[2], color[1], color[0])

    def __isAllBlack(self):
        isLeftRoomBlack = self.__hasColor(
            (0, 0, 0), *self.__getPositionByDirection(Direction.LEFT, self.offsetRoom))
        isTopRoomBlack = self.__hasColor(
            (0, 0, 0), *self.__getPositionByDirection(Direction.TOP, self.offsetRoom))
        isRightRoomBlack = self.__hasColor(
            (0, 0, 0), *self.__getPositionByDirection(Direction.RIGHT, self.offsetRoom))
        isBottomRoomBlack = self.__hasColor(
            (0, 0, 0), *self.__getPositionByDirection(Direction.BOTTOM, self.offsetRoom))
        return isLeftRoomBlack and isTopRoomBlack and isRightRoomBlack and isBottomRoomBlack

    def __getPositionByDirection(self, d: Direction, offset):
        cx, cy = self.center[0], self.center[1]
        if d == Direction.LEFT:
            return cx-offset, cy
        elif d == Direction.TOP:
            return cx, cy-offset
        elif d == Direction.RIGHT:
            return cx+offset, cy
        elif d == Direction.BOTTOM:
            return cx, cy+offset
        elif d == Direction.LEFT_TOP:
            return cx-offset, cy-offset
        elif d == Direction.LEFT_BOTTOM:
            return cx-offset, cy+offset
        elif d == Direction.RIGHT_TOP:
            return cx+offset, cy-offset
        elif d == Direction.RIGHT_BOTTOM:
            return cx+offset, cy+offset

    # 箭头是否指向某个方向
    def __hasArrow(self, d: Direction):
        x, y = self.__getPositionByDirection(d, self.offsetArrow)
        return self.__hasColor(self.arrowColor, x, y)

    # 某个方向是否有Buff
    def __hasBuff(self, d: Direction):
        x, y = self.__getPositionByDirection(d, self.offsetRoom)
        return self.__hasColor(self.buffColor, x, y)

    # 某个方向是否有精英怪
    def __hasMoster(self, d: Direction):
        x, y = self.__getPositionByDirection(d, self.offsetRoom)
        return self.__hasColor(self.mosterColor, x, y)

    # 是否清理某个方向的房间
    def __hasGone(self, d: Direction):
        x, y = self.__getPositionByDirection(d, self.offsetRoom)
        return self.__hasColor(self.wayColor, x, y)

    # 从输入图像矩阵识别当前房间号
    def parseRoomNum(self, img0):
        if img0 is None:
            return None
        if img0.shape[0] > img0.shape[1]:
            print("竖屏模式，忽略")
            return None
        # 清除搜索缓存
        self.searchCache.clear()
        self.img = img0
        roomNum = -2
        if self.__hasArrow(Direction.BOTTOM) and (self.__hasGone(Direction.RIGHT) or self.__hasBuff(Direction.RIGHT) or self.__hasMoster(Direction.RIGHT)):
            # 箭头朝下，且右边房间已清理或有Buff或有精英怪
            roomNum = 0
        elif not self.__hasGone(Direction.LEFT) and not self.__hasGone(Direction.LEFT_TOP) and not self.__hasGone(Direction.LEFT_BOTTOM) and self.__hasGone(Direction.TOP) and self.__hasArrow(Direction.RIGHT):
            # 左边3个房间都没清理，且上面房间清理，且箭头朝右
            roomNum = 1
        elif self.__hasGone(Direction.LEFT) and self.__hasGone(Direction.LEFT_TOP) and not self.__hasGone(Direction.LEFT_BOTTOM) and self.__hasArrow(Direction.RIGHT):
            # 左边和左上房间清理，且左下方没清理，且箭头朝右
            roomNum = 2
        elif self.__hasGone(Direction.LEFT) and self.__hasArrow(Direction.TOP):
            # 左边房间清理，且小箭头朝上
            roomNum = 3
        elif self.__hasGone(Direction.BOTTOM) and (not self.__hasGone(Direction.RIGHT_BOTTOM) and not self.__hasBuff(Direction.RIGHT_BOTTOM) and not self.__hasMoster(Direction.RIGHT_BOTTOM)) and self.__hasArrow(Direction.RIGHT):
            # 下面房间清理，且右下房间没清理且没Buff没精英怪，且小箭头朝右
            roomNum = 4
        elif self.__hasGone(Direction.BOTTOM) and self.__hasGone(Direction.LEFT_BOTTOM) and self.__hasGone(Direction.RIGHT_BOTTOM) and self.__hasArrow(Direction.RIGHT):
            # 狮子头，下方3个房间都清理，且小箭头朝右
            roomNum = 5
        elif self.__hasGone(Direction.LEFT) and self.__hasGone(Direction.LEFT_BOTTOM) and not self.__hasGone(Direction.BOTTOM):
            # 左边和左下房间清理，且下方没清理
            roomNum = 6
        elif self.__hasGone(Direction.LEFT) and not self.__hasGone(Direction.LEFT_TOP) and not self.__hasGone(Direction.LEFT_BOTTOM) and self.__hasArrow(Direction.RIGHT):
            # 左边房间清理，左上左下没清理，且箭头朝右
            roomNum = 7
        elif (not self.__hasArrow(Direction.TOP) and not self.__hasArrow(Direction.RIGHT) and not self.__hasArrow(Direction.BOTTOM)) and (self.__hasGone(Direction.LEFT) or self.__hasBuff(Direction.LEFT)):
            # 上右下都没有箭头 && （左边房间清理 || 左边房间有Buff）
            roomNum = 8
        elif self.__hasGone(Direction.BOTTOM) and self.__hasArrow(Direction.RIGHT) and (self.__hasGone(Direction.RIGHT_BOTTOM) or self.__hasBuff(Direction.RIGHT_BOTTOM) or self.__hasMoster(Direction.RIGHT_BOTTOM)):
            # 下面房间清理，且小箭头朝右，且右下房间已清理或有Buff或有精英怪
            roomNum = 9
        elif self.__hasArrow(Direction.BOTTOM) and self.__hasGone(Direction.BOTTOM):
            # 下方房间清理过，并且箭头朝下
            roomNum = 10
        elif self.__isAllBlack():
            # 全黑，过图中
            roomNum = -1
        else:
            # 没有检查到任何已经定义的房间
            roomNum = -2
        # Issue:在黑屏渐变期间，有概率会把4号房识别成8号房，虽然渐变完后会自行恢复成4号，这里还是特色处理一下
        # Workarround: 设备出8号房的时候，额外判断下如果没去过7号房就返回-2
        if roomNum == 8 and 7 not in self.cleanedRoom:
            roomNum = -2
        if roomNum == 0 and not self.__hasGone(Direction.TOP) and not self.__hasGone(Direction.BOTTOM):
            self.cleanedRoom.clear()
        if roomNum >= 0:
            if roomNum in self.cleanedRoom:
                self.cleanedRoom.pop(roomNum)
            self.cleanedRoom[roomNum] = True
        return roomNum

    # 查找以point为中心，半径为r的矩形区域内是否有指定颜色
    # color:要查找的颜色
    # point:指定屏幕坐标
    # r:区域半径
    def __findColorFormArea(self, color, x, y, r=5):
        matrix = self.img
        if x+r > matrix.shape[1]:
            print("设定的坐标X轴超过画布")
            return None
        if y+r > matrix.shape[0]:
            print("设定的坐标Y轴超过画布")
            return None
        # 定义内部返回函数

        def result(screenColor):
            if self.__areColorsSimilar(screenColor, color):
                return screenColor

        ########################################################
        # 螺旋矩阵算法，从中心点向外一层一层遍历
        # 中心点出现指定颜色的概率更高，所以从中心点螺旋向外遍历矩阵
        # 查找到指定颜色后中断遍历
        #
        # 最大圈数（中心点外有几圈）
        maxCircleNum = r
        # 初始化当前位置到中心点
        nowX, nowY = x, y
        # 第一步固定为中心点
        value = result(self.__getColor(nowX, nowY))
        if value:
            return value
        # 如果一圈都没有（只有中心点），直接返回
        if maxCircleNum == 0:
            return
        # 从第一圈遍历到最大圈
        for circleNum in fromTo(1, maxCircleNum):
            # 先向右一像素
            value = result(self.__getColor(nowX+1, nowY,))
            if value:
                return value
            nowX += 1
            # 向下走(圈数*2-1)像素
            for i in fromTo(1, circleNum*2-1):
                value = result(self.__getColor(nowX, nowY+i))
                if value:
                    return value
            nowY += circleNum*2-1
            # 向左走圈数*2像素
            for i in fromTo(1, circleNum*2):
                value = result(self.__getColor(nowX-i, nowY))
                if value:
                    return value
            nowX -= circleNum*2
            # 向上走圈数*2像素
            for i in fromTo(1, circleNum*2):
                value = result(self.__getColor(nowX, nowY-i))
                if value:
                    return value
            nowY -= circleNum*2
            # 向右走圈数*2像素
            for i in fromTo(1, circleNum*2):
                value = result(self.__getColor(nowX+i, nowY))
                if value:
                    return value
            nowX += circleNum*2
        #
        # 结束遍历
        ########################################################

    def drawMap(self, image):
        r = int(self.rate * 5)
        x, y = self.center
        off = self.offsetRoom
        cv2.circle(image, (x+off, y+off), r, (0, 0, 255), -1)
        cv2.circle(image, (x+off, y-off), r, (0, 0, 255), -1)
        cv2.circle(image, (x-off, y+off), r, (0, 0, 255), -1)
        cv2.circle(image, (x-off, y-off), r, (0, 0, 255), -1)
        cv2.circle(image, (x, y+off), r, (0, 0, 255), -1)
        cv2.circle(image, (x, y-off), r, (0, 0, 255), -1)
        cv2.circle(image, (x+off, y), r, (0, 0, 255), -1)
        cv2.circle(image, (x-off, y), r, (0, 0, 255), -1)
        cv2.circle(image, (x, y), r, (0, 0, 255), -1)
        cv2.circle(image, (x, y+self.offsetArrow), r, (0, 0, 255), -1)
        cv2.circle(image, (x, y-self.offsetArrow), r, (0, 0, 255), -1)
        cv2.circle(image, (x+self.offsetArrow, y), r, (0, 0, 255), -1)
        cv2.circle(image, (x-self.offsetArrow, y), r, (0, 0, 255), -1)

    # 绘制一张可视化小地图
    def drawMiniMap(self, image):
        # 根据屏幕大小计算绘制参数
        lines = (3, 6, 3)
        height, width, _ = image.shape
        w = int(width*0.015)
        margin = int(w * 0.3)
        wMax = w * 6 + margin * 5
        hMax = w * 3 + margin * 2
        startX = (width - wMax) // 2
        startY = height // 40
        endX = startX + wMax
        endY = startY + hMax
        # 创建一张有alpha通道的空画布，并绘制小地图
        map = {0:9,1:-2,2:10,3:0,4:5,5:4,6:6,7:7,8:8,9:1,10:2,11:3}
        n = 0
        overlay = np.zeros((hMax, wMax, 4), np.uint8)
        for i in range(0, len(lines)):
            y = i*(w+margin)
            for j in range(0, lines[i]):
                x = j*(w+margin)
                if map[n] in self.cleanedRoom:
                    color = (155,155,155,180)
                elif n == 4:
                    color = (3, 99, 186, 180)
                elif n == 8:
                    color = (0, 0, 158, 180)
                else:
                    color = (33, 33, 33, 180)
                cv2.rectangle(overlay, (x, y), (x + w, y + w), color, -1)
                if len(self.cleanedRoom)>0:
                    roomNow = deque(self.cleanedRoom.keys(), maxlen=1)[0]
                    nNow = next(key for key, value in map.items() if value == roomNow)
                    if n == nNow:
                        direction = self.direction
                        if direction == Direction.LEFT:
                            end_point = (int(x + w*0.2), y + w//2)
                            start_point = (int(x + w*0.8), y + w//2)
                        elif direction == Direction.RIGHT:
                            start_point = (int(x + w*0.2), y + w//2)
                            end_point = (int(x + w*0.8), y + w//2)
                        elif direction == Direction.TOP:
                            start_point = ((x + w//2), int(y + w*0.8))
                            end_point = ((x + w//2), int(y + w*0.2))
                        elif direction == Direction.BOTTOM:
                            start_point = ((x + w//2), int(y + w*0.2))
                            end_point = ((x + w//2), int(y + w*0.8))
                        if direction:
                            cv2.arrowedLine(overlay, start_point, end_point, (255, 0, 0, 0), thickness = 1, tipLength=0.5)
                n += 1
        # 叠加到原图
        alpha = overlay[:, :, 3] / 255.0
        blended_region = (1 - alpha[:, :, None]) * image[startY:endY,
                                                         startX:endX] + alpha[:, :, None] * overlay[:, :, :3]
        image[startY:endY, startX:endX] = blended_region.astype(np.uint8)


# 生成区间:左闭右闭
def fromTo(i, j):
    return range(i, j+1)


def log(*text):
    if False:
        print(*text)


roomHelper = BWJRoomHelper()

if __name__ == '__main__':
    import cv2
    img = cv2.imread('test/screen1.jpg')
    roomNum = roomHelper.parseRoomNum(img)
    print("roomNum", roomNum)
