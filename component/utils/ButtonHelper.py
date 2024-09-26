import cv2
from config import JITTER
import component.utils.RuntimeData as R

class ButtonHelper(object):
    def __init__(self):
        pass

    def drawButtons(self, img, skillData):
        scale = R.SCALE
        jitter = int(JITTER*scale)
        for key, value in skillData.items():
            if key == "joystick":
                radius = int(value["radius"]*scale)
                value = value["center"]
                centerArea = (int(value[0]*scale), int(value[1]*scale))
                cv2.circle(img, centerArea, radius, (0, 0, 255), 2)
            if isinstance(value, str):
                continue
            center = (int(value[0]*scale), int(value[1]*scale))
            cv2.circle(img, center, jitter, (0, 0, 255), -1)
            cv2.putText(img, key, center, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1,lineType = cv2.LINE_AA)


buttonHelper = ButtonHelper()