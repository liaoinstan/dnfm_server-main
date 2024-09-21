import cv2
import numpy as np

# 读取模板和图像
template = cv2.imread('test/small.jpg')
image = cv2.imread('test/big.jpg')

# 使用模板匹配
result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

# 设置阈值
threshold = 0.8
loc = np.where(result >= threshold)

# 获取匹配结果的坐标和匹配值
points = list(zip(*loc[::-1]))

# 使用轮廓检测和边界框合并
rectangles = []
for point in points:
    x, y = point
    rectangles.append([x, y, template.shape[1], template.shape[0]])

rectangles, weights = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.2)
print("size",len(rectangles))

# 在匹配结果图像上绘制合并后的结果
result_merged = image.copy()
for (x, y, w, h) in rectangles:
    cv2.rectangle(result_merged, (x, y), (x + w, y + h), (255, 0, 0), 2)

cv2.imshow('Result with Merged Rectangles', result_merged)
cv2.waitKey(0)
cv2.destroyAllWindows()
