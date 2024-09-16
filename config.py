
########################################################
# 窗口分辨率配置
#
# 古董电脑降低窗口分辨率可以降低性能消耗
# 设置成 0 会使用和手机一样的分辨率
# 电脑不是太差的可以配置 0
#
WINDOW_WIDTH = 1000
#
########################################################


########################################################
# 小地图房间识别识别配置
#
# 先配置下面两个参数，然后运行游戏，可以看到小地图上的小红点
# 外围小红点必须对齐每个房间中心，否则房间识别不准确
# 调整下面两个参数直到完全对齐为止
# 以下是我的手机(3200*1440)的参数供参考
#
# 小地图中心点坐标（蓝色小人）
CENTER_POINT = (2950, 174)
# 小地图中心点距相邻房间中心点距离（=房间直径）
OFFSET_ROOM = 77
#
########################################################


########################################################
# 卡位补救措施
#
# 卡位超时时间：毫秒
#（超过这个时间无法进门会被判定为卡位，并执行补救措施）
# 补救算法：
# 随机朝一个方向移动一段距离，可能需要多次触发才能脱离卡位
# 比如：走进了一个只能往下走才能出来的角落，卡位补救超时触发
# 随机的方向是上方，就会再过5秒再随机一次，直到随机到下方
#
BLOCKER_TIME_OUT = 5000
#
########################################################


########################################################
# 再次挑战点击坐标
#
# 暂时还没写，先配个坐标再说
#
AGAIN = (2814, 189)
GOHOME = (2814, 482)
#
########################################################


########################################################
# 技能配置
#
# 运行辅助程序 test/location.py 检查坐标是否正确
#
########################################################