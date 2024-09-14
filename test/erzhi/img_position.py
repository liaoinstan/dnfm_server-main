import cv2

# 读取图片
image = cv2.imread('test/erzhi/lan_out.jpg')

# 转换为灰度图像
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 使用阈值处理将白色区域提取出来
_, thresholded = cv2.threshold(gray_image, 30, 255, cv2.THRESH_BINARY)

# cv2.imshow("Binary Image", thresholded)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# 找出白色区域的轮廓
contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 计算白色区域的中心位置坐标
if len(contours) > 0:
    contour = contours[0]
    M = cv2.moments(contour)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    print("蓝色区域的中心位置坐标：({}, {})".format(cX, cY))
    
    image = cv2.imread('test/erzhi/1.jpg')
    center = (cX, cY)  # 指定圆心位置为(100, 100)
    radius = 5  # 指定半径为5
    # 画一个红色小圆点
    color = (0, 0, 255)  # 红色 (BGR颜色表示)
    thickness = -1  # 填充圆形
    cv2.circle(image, center, radius, color, thickness)
    # 显示图片
    cv2.imshow('Image with Red Dot', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()