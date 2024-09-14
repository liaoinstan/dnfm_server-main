import cv2
import numpy as np

# 读取图像
image = cv2.imread("test/erzhi/1.jpg")

# 将图像转换为HSV颜色空间
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义蓝色的HSV范围
lower_green = np.array([90, 50, 50])
upper_green = np.array([130, 255, 255])

#48 236 245

# lower_green = np.array([38, 186, 195])
# upper_green = np.array([58, 255, 255])


# 根据蓝色的HSV范围创建掩码
mask = cv2.inRange(hsv_image, lower_green, upper_green)

# 对原始图像应用掩码，提取蓝色区域
blue_image = cv2.bitwise_and(image, image, mask=mask)

cv2.imwrite("test/erzhi/lan_out.jpg", blue_image)

# 显示提取出的蓝色区域
cv2.imshow("Blue Filtered Image", blue_image)
cv2.waitKey(0)
cv2.destroyAllWindows()