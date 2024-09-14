import cv2
import json
import numpy as np
import os


########################################################
#
# 运行这个程序用来检查你的键位配置
# 这里填你的屏幕分辨率
SCREEN = (1440, 3200)
# 缩放, 0-1 随便填, 预览窗口小了改大，大了改小
SCALE = 0.5
#
########################################################

# 读取配置
current_dir = os.path.dirname(os.path.abspath(__file__))
skill_file_path = os.path.join(current_dir, "../skill.json")
with open(skill_file_path, 'r', encoding='utf-8') as file:
    skillData = json.load(file)


# 显示
canvas = np.zeros((int(SCREEN[0]*SCALE), int(SCREEN[1]*SCALE), 3), dtype=np.uint8)
print(canvas.shape)
for key, value in skillData.items():
    if key == "joystick":
        value = value["center"]
    if isinstance(value, str):
        continue
    print(key, value)
    center = (int(value[0]*SCALE), int(value[1]*SCALE))
    cv2.circle(canvas, center, 10, (0, 0, 255), -1)
    cv2.putText(canvas, key, center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
cv2.imshow('Canvas', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
