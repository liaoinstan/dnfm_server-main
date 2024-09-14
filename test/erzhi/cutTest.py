import cv2

# 读取图片
image = cv2.imread('test/screen1.jpg')

# 获取图片的高度和宽度
height, width = image.shape[:2]

w,h = 450,400
cropped_image = image[0:h, width - w:width]

# 显示裁剪后的图片
cv2.imshow('Cropped Image', cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()