import cv2
import numpy as np

def getHSVColorPosition(image, lower, upper):
    # 将图像转换为HSV颜色空间
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # 根据指定的的HSV范围创建掩码
    mask = cv2.inRange(hsv_image, np.array(lower), np.array(upper))
    # 对原始图像应用掩码，提取指定色域
    black_image = cv2.bitwise_and(image, image, mask=mask)
    # 转换为灰度图像
    gray_image = cv2.cvtColor(black_image, cv2.COLOR_BGR2GRAY)
    # 使用阈值处理将白色区域提取出来
    _, thresholded = cv2.threshold(gray_image, 30, 255, cv2.THRESH_BINARY)
    # 找出白色区域的轮廓
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 计算白色区域的中心位置坐标
    if len(contours) > 0:
        contour = contours[0]
        M = cv2.moments(contour)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        print("色域区域的中心位置坐标：({}, {})".format(cX, cY))
        return cX, cY
    else:
        print("未提取到轮廓")
        
        
if __name__ == '__main__':
    
    image = cv2.imread("test/erzhi/1.jpg")
        
    bx,by = getHSVColorPosition(image, [90, 50, 50], [130, 255, 255])
    gx,gy = getHSVColorPosition(image, [38, 186, 195], [58, 255, 255])

    cv2.circle(image, (bx,by), 5, (0, 0, 255), -1)
    cv2.circle(image, (gx,gy), 5, (0, 0, 255), -1)
    
    OFFSET_ARROW = max(abs(by - gy),abs(bx - gx))
    
    OFFSET_ROOM = int(OFFSET_ARROW/0.64)
    print("OFFSET_ARROW",OFFSET_ARROW,"OFFSET_ROOM",OFFSET_ROOM)
    cv2.circle(image, (bx,by-OFFSET_ROOM), 5, (0, 0, 255), -1)

    cv2.imshow('Image with Red Dot', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
