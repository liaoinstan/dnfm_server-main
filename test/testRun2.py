import numpy as np


def generate_matrix(center, R):
    x = center[0]
    y = center[1]
    matrix = np.empty((2*R+1, 2*R+1), dtype=tuple)
    for i in range(2*R+1):
        for j in range(2*R+1):
            matrix[i, j] = (x-R+i, y-R+j)  # 修改这里让matrix[x,y]能获取坐标
    return matrix

# step2:统计相关指标及初始化存储列表


def w2n(matrix):
    rows = len(matrix)
    cols = len(matrix[0])

    left = 0
    right = cols - 1
    top = 0
    bottom = rows - 1

    result = []

    # step3:循环遍历，顺时针读取存储矩阵元素
    while left <= right and top <= right:
        # 行-从左到右（left,right）
        for col in range(left, right+1):
            result.append(matrix[top][col])
        # 列-从上到下（top+1,bottom）
        for row in range(top+1, bottom+1):
            result.append(matrix[row][right])

        # 若行与列不等则继续以下遍历
        if left < right and top < bottom:
            # 行-从右到左（right-1,left+1,-1）下角标从右边开始读取
            for col in range(right-1, left, -1):
                result.append(matrix[bottom][col])
            # 列-从下到上（bottom,top+1,-1）
            for row in range(bottom, top, -1):
                result.append(matrix[row][left])

        # 每循环一次外层循环后更新一次相关变量，进入下一内层循环
        left += 1
        right -= 1
        top += 1
        bottom -= 1

    return result


def fromTo(i, j):
    return range(i, j+1)


def n2w(matrix):
    height, width = matrix.shape
    if width != height:
        print("矩阵不合法，长宽不等")
        return
    if width % 2 == 0:
        print("矩阵不合法，没有中心点")
        return
    def result(ele):
        print(ele)
        return
    # 矩阵长度
    length = width
    # 最大圈数（中心点外有几圈）
    maxCircleNum = length // 2
    # 初始化当前位置到中心点
    nowX, nowY = maxCircleNum, maxCircleNum
    # 第一步固定为中心点
    result(matrix[nowX][nowY])
    # 如果一圈都没有（只有中心点），直接返回
    if maxCircleNum == 0:
        return
    # 从第一圈遍历到最大圈
    for circleNum in fromTo(1,maxCircleNum):
        # 先向右一步
        result(matrix[nowX+1][nowY])
        nowX += 1
        # 向下走(圈数*2-1)步
        for i in fromTo(1, circleNum*2-1):
            result(matrix[nowX, nowY+i])
        nowY += circleNum*2-1
        # 向左走圈数*2步
        for i in fromTo(1, circleNum*2):
            result(matrix[nowX-i, nowY])
        nowX -= circleNum*2
        # 向上走圈数*2步
        for i in fromTo(1, circleNum*2):
            result(matrix[nowX, nowY-i])
        nowY -= circleNum*2
        # 向右走圈数*2步
        for i in fromTo(1, circleNum*2):
            result(matrix[nowX+i, nowY])
        nowX += circleNum*2


if __name__ == '__main__':

    # 生成数组
    matrix = generate_matrix((10, 10), 3)

    # 打印数组
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[0]):
            print(str(matrix[j, i]).rjust(8), end=' ')
        print("")

    # print(w2n(matrix2))
    n2w(matrix)
