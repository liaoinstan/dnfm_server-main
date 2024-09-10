import cv2
import json
import numpy as np

# 读取Json文件
# with open('data.json') as f:
    # data = json.load(f)
    
data = {
    "center": [294,556],
    "attack":[1441,671],
    "Jump_Back":[1345,693],
    "Jump":[1500,545],
    "Roulette":[1365,372],
    "skill1":[1484,474],
    "skill2":[1153,690],
    "skill3": [1250,678],
    "skill4": [1402,254],
    "skill5":[1486, 351],
    "skill6":[1368, 485],
    "skill7":[1214, 584],
    "skill8":[1032, 684],
    "skill9":[1250, 263],
    "skill10":[1438, 653],
    "skill11":[1336, 263],
    "skill15":[1554,194]
}

# 创建一个空白画布
canvas = np.zeros((720, 1800, 3), dtype=np.uint8)

# 在画布上绘制文字
for key, value in data.items():
    cv2.putText(canvas, key, tuple(value), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # 绘制白色文字

# 显示画布
cv2.imshow('Canvas', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()