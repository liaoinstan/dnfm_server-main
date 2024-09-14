import cv2
import json
import numpy as np

# 读取Json文件
# with open('data.json') as f:
    # data = json.load(f)
scale = 0.5
screen = (1440, 3200)
    
data = {
    "center": [593, 1047],
    "attack":[2832,1273],
    "Jump_Back":[2631,1290],
    "Jump":[2941,1133],
    "Roulette":[2842,966],
    "skill4":[2324,1132],
    "skill7":[2036,1294],
    "skill1": [2430,1294],
    "skill10": [1621,1289],
    "skill5":[2237,1294],
    "skill3":[2723,1132],
    "skill2":[2520,1132],
    "skill6":[2123,1132],
    "skill8":[1335,1289],
    "skill11":[1773,1289],
    "skill9":[1478,1289]
}

# 创建一个空白画布
canvas = np.zeros((int(screen[0]*scale), int(screen[1]*scale), 3), dtype=np.uint8)

# 在画布上绘制文字
for key, value in data.items():
    center = (int(value[0]*scale),int(value[1]*scale))
    cv2.circle(canvas, center, 10, (0, 0, 255), -1)
    cv2.putText(canvas, key, center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # 绘制白色文字

# 显示画布
cv2.imshow('Canvas', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()