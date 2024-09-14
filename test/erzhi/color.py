import colorsys

# 将RGB颜色值转换为HSV颜色值
r, g, b = 104, 245, 18
h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

# 将HSV颜色值转换为OpenCV的格式
h = int(h * 179)  # 色相范围是0-179
s = int(s * 255)  # 饱和度范围是0-255
v = int(v * 255)  # 亮度范围是0-255

print(h,s,v)