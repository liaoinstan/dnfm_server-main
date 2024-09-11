import math
from enum import Enum

########################################################
#   以下参数需要根据自己设备进行调整
#   屏幕坐标可以在开发者选项中打开"指针位置"获取屏幕坐标
#
#
# 小地图中心点坐标（蓝色小人）
CENTER_POINT = (2954, 174)
# 小地图中心点距相邻房间中心点距离（=房间直径）
OFFSET_ROOM = 77
# 小地图中心点距地图绿色小箭头中心点距离
OFFSET_ARROW = 53
# 游戏窗口宽度（画布宽） / 设备屏幕真实宽度(屏幕分辨率)
RATE = 800 / 3200
#
########################################################


def convet(x):
    return int(x*RATE)


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
        self.center = (convet(CENTER_POINT[0]), convet(CENTER_POINT[1]))
        self.offsetRoom = convet(OFFSET_ROOM)
        self.offsetArrow = convet(OFFSET_ARROW)
        self.img = None
        # 已走过的道路的颜色，用于区分小地图的房间是否已经清理
        self.wayColor = (211, 183, 128)
        # 小地图箭头颜色，用于识别小地图箭头朝向
        self.arrowColor = (99, 250, 14)
        # Buff图标颜色
        self.buffColor = (9, 154, 55)

    # 计算两个RGB颜色之间的欧氏距离，距离代表相似度，越小越相似
    def euclideanColorDistance(self, color1, color2):
        return math.sqrt((color1[0] - color2[0])**2 + (color1[1] - color2[1])**2 + (color1[2] - color2[2])**2)

    # 判断两个RGB颜色是否大致相等，threshold越小相似度越高
    def areColorsSimilar(self, color1, color2, threshold=30):
        distance = self.euclideanColorDistance(color1, color2)
        if distance < 30:
            return True
        else:
            return False

    def isWay(self, color):
        return self.areColorsSimilar(color, self.wayColor)

    def isArrow(self, color):
        return self.areColorsSimilar(color, self.arrowColor)

    def isBuff(self, color):
        return self.areColorsSimilar(color, self.buffColor)

    def isBlack(self, color):
        return self.areColorsSimilar(color, (0, 0, 0))

    def getColor(self, x, y):
        # 横屏模式下图片为(h,w,3)先取Y轴再取X轴
        return self.BGR2RGB(self.img[y, x])

    def BGR2RGB(self, color):
        return (color[2], color[1], color[0])

    def isAllBlack(self):
        return self.isBlack(self.getRoomColor(Direction.LEFT)) and self.isBlack(self.getRoomColor(Direction.TOP)) and self.isBlack(self.getRoomColor(Direction.RIGHT)) and self.isBlack(self.getRoomColor(Direction.BOTTOM))

    def getRoomColor(self, d: Direction):
        cx, cy = self.center[0], self.center[1]
        if d == Direction.LEFT:
            # print("img.shape", self.img.shape)
            return self.getColor(cx-self.offsetRoom, cy)
        elif d == Direction.TOP:
            return self.getColor(cx, cy-self.offsetRoom)
        elif d == Direction.RIGHT:
            return self.getColor(cx+self.offsetRoom, cy)
        elif d == Direction.BOTTOM:
            return self.getColor(cx, cy+self.offsetRoom)
        elif d == Direction.LEFT_TOP:
            return self.getColor(cx-self.offsetRoom, cy-self.offsetRoom)
        elif d == Direction.LEFT_BOTTOM:
            return self.getColor(cx-self.offsetRoom, cy+self.offsetRoom)
        elif d == Direction.RIGHT_TOP:
            return self.getColor(cx+self.offsetRoom, cy-self.offsetRoom)
        elif d == Direction.RIGHT_BOTTOM:
            return self.getColor(cx+self.offsetRoom, cy+self.offsetRoom)

    # 箭头是否指向某个方向
    def hasArrow(self, d: Direction):
        cx, cy = self.center[0], self.center[1]
        if d == Direction.LEFT:
            return self.isArrow(self.getColor(cx-self.offsetArrow, cy))
        elif d == Direction.TOP:
            return self.isArrow(self.getColor(cx, cy-self.offsetArrow))
        elif d == Direction.RIGHT:
            return self.isArrow(self.getColor(cx+self.offsetArrow, cy))
        elif d == Direction.BOTTOM:
            return self.isArrow(self.getColor(cx, cy+self.offsetArrow))

    # 某个方向是否有Buff
    def hasBuff(self, d: Direction):
        cx, cy = self.center[0], self.center[1]
        if d == Direction.LEFT:
            return self.isBuff(self.getColor(cx-self.offsetRoom, cy))
        elif d == Direction.TOP:
            return self.isBuff(self.getColor(cx, cy-self.offsetRoom))
        elif d == Direction.RIGHT:
            return self.isBuff(self.getColor(cx+self.offsetRoom, cy))
        elif d == Direction.BOTTOM:
            return self.isBuff(self.getColor(cx, cy+self.offsetRoom))

    # 是否清理某个方向的房间
    def hasGone(self, d: Direction):
        return self.isWay(self.getRoomColor(d))

    def parseRoomNum(self, img0):
        if img0 is None:
            return None
        if img0.shape[0] > img0.shape[1]:
            print("竖屏模式，忽略")
            return None
        self.img = img0
        if not self.hasGone(Direction.LEFT) and not self.hasGone(Direction.LEFT_TOP) and not self.hasGone(Direction.LEFT_BOTTOM) and self.hasArrow(Direction.BOTTOM):
            # 左边3个房间都没清理，且箭头朝下
            return 0
        elif not self.hasGone(Direction.LEFT) and not self.hasGone(Direction.LEFT_TOP) and not self.hasGone(Direction.LEFT_BOTTOM) and self.hasGone(Direction.TOP) and self.hasArrow(Direction.RIGHT):
            # 左边3个房间都没清理，且上面房间清理，且箭头朝右
            return 1
        elif self.hasGone(Direction.LEFT) and self.hasGone(Direction.LEFT_TOP) and not self.hasGone(Direction.LEFT_BOTTOM) and self.hasArrow(Direction.RIGHT):
            # 左边和左上房间清理，且左下方没清理，且箭头朝右
            return 2
        elif self.hasGone(Direction.LEFT) and self.hasArrow(Direction.TOP):
            # 左边房间清理，且小箭头朝上
            return 3
        elif self.hasGone(Direction.BOTTOM) and not self.hasGone(Direction.RIGHT_BOTTOM) and self.hasArrow(Direction.RIGHT):
            # 下面房间清理，且右下房间没清理，且小箭头朝右
            return 4
        elif self.hasGone(Direction.BOTTOM) and self.hasGone(Direction.LEFT_BOTTOM) and self.hasGone(Direction.RIGHT_BOTTOM):
            # 狮子头，下方3个房间都清理
            return 5
        elif self.hasGone(Direction.LEFT) and self.hasGone(Direction.LEFT_BOTTOM) and not self.hasGone(Direction.BOTTOM):
            # 左边和左下房间清理，且下方没清理
            return 6
        elif self.hasGone(Direction.LEFT) and not self.hasGone(Direction.LEFT_TOP) and not self.hasGone(Direction.LEFT_BOTTOM) and self.hasArrow(Direction.RIGHT):
            # 左边房间清理，左上左下没清理，且箭头朝右
            return 7
        elif (not self.hasArrow(Direction.TOP) and not self.hasArrow(Direction.RIGHT) and not self.hasArrow(Direction.BOTTOM)) and (self.hasGone(Direction.LEFT) or self.hasBuff(Direction.LEFT)):
            # 上右下都没有箭头 && （左边房间清理 || 左边房间有Buff）
            return 8
        elif self.isAllBlack():
            # 全黑，过图中
            return -1
        else:
            # 其他房间都不是，走错路了，跟着箭头返回
            return -2


roomHelper = BWJRoomHelper()

if __name__ == '__main__':
    import cv2
    img = cv2.imread('./screen1.jpg')
    roomNum = roomHelper.parseRoomNum(img)
    print("roomNum", roomNum)
