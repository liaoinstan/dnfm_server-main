import cv2
import numpy as np
from config import WINDOW_WIDTH
import time

DEBUG = False


def getHSVColorPosition(image, lower, upper):
    try:
        # 将图像转换为HSV颜色空间
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # 根据指定的的HSV范围创建掩码
        mask = cv2.inRange(hsv_image, np.array(lower), np.array(upper))
        # 对原始图像应用掩码，提取指定色域
        color_image = cv2.bitwise_and(image, image, mask=mask)

        if DEBUG:
            cv2.imshow('color_image', color_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # 转换为灰度图像
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        # 使用阈值处理将白色区域提取出来
        _, thresholded = cv2.threshold(gray_image, 70, 255, cv2.THRESH_BINARY)

        if DEBUG:
            cv2.imshow('gray_image', thresholded)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # 找出白色区域的轮廓
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 计算白色区域的中心位置坐标
        center_x = 0
        center_y = 0
        valid_contour_count = 0

        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                center_x += cX
                center_y += cY
                valid_contour_count += 1

        center_x = int(center_x / valid_contour_count)
        center_y = int(center_y / valid_contour_count)

        return center_x, center_y
    except Exception as e:
        print("图像处理异常:", e)
        return None, None


def convert(x):
    RATE = WINDOW_WIDTH/3200
    return int(x*RATE)


def drawMap(image):

    height, width = image.shape[:2]
    w, h, margin = convert(400), convert(300), convert(90)
    cropped_image = image[0:h, width - w:width-margin]

    if DEBUG:
        cv2.imshow('cropped_image', cropped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    s = time.time()
    bx, by = getHSVColorPosition(cropped_image, [79, 100, 200], [118, 255, 255])
    # print(f'找地图点耗时{(time.time() - s) * 1000} ms')
    gx, gy = getHSVColorPosition(cropped_image, [38, 186, 195], [58, 255, 255])

    if not bx or not by or not gx or not gy:
        return
    OFFSET_ARROW = max(abs(by - gy), abs(bx - gx))
    OFFSET_ROOM = int(OFFSET_ARROW/0.64)
    print("OFFSET_ARROW", OFFSET_ARROW, "OFFSET_ROOM", OFFSET_ROOM)

    xOffset = width - w
    r = convert(5)

    cv2.circle(image, (xOffset+bx, by), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+gx, gy), r, (0, 0, 255), -1)

    cv2.circle(image, (xOffset+bx, by-OFFSET_ROOM), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+bx, by+OFFSET_ROOM), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+bx-OFFSET_ROOM, by), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+bx+OFFSET_ROOM, by), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+bx-OFFSET_ROOM, by-OFFSET_ROOM), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+bx+OFFSET_ROOM, by+OFFSET_ROOM), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+bx-OFFSET_ROOM, by+OFFSET_ROOM), r, (0, 0, 255), -1)
    cv2.circle(image, (xOffset+bx+OFFSET_ROOM, by-OFFSET_ROOM), r, (0, 0, 255), -1)


if __name__ == '__main__':
    WINDOW_WIDTH = 3200
    # image = cv2.imread("test/erzhi/1.jpg")
    image = cv2.imread("test/screen1.jpg")

    drawMap(image)

    resized_image = cv2.resize(image, (int(image.shape[1]/2), int(image.shape[0]/2)), interpolation=cv2.INTER_AREA)

    cv2.imshow('Image with Red Dot', resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
