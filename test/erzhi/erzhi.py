import cv2

# 读取图片
image = cv2.imread("test/erzhi/1.jpg", cv2.IMREAD_GRAYSCALE)

# 对图片进行二值化处理
threshold = 60
_, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)

# 保存二值化后的图片
# cv2.imwrite("test/erzhi/erzhi_out.jpg", binary_image)

# 显示二值化后的图片
cv2.imshow("Binary Image", binary_image)
cv2.waitKey(0)
cv2.destroyAllWindows()