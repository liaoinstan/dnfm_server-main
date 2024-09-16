import cv2
from config import SHOW_BUTTON
from config import JITTER

class ButtonHelper(object):
    def __init__(self):
        self.scale = 1

    def init(self, scale):
        self.scale = scale

    def drawButtons(self, img, skillData):
        if not SHOW_BUTTON:
            return
        jitter = int(JITTER*self.scale)
        for key, value in skillData.items():
            if key == "joystick":
                radius = int(value["radius"]*self.scale)
                value = value["center"]
                centerArea = (int(value[0]*self.scale), int(value[1]*self.scale))
                cv2.circle(img, centerArea, radius, (0, 0, 255), 2)
            if isinstance(value, str):
                continue
            center = (int(value[0]*self.scale), int(value[1]*self.scale))
            cv2.circle(img, center, jitter, (0, 0, 255), -1)
            cv2.putText(img, key, center, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1,lineType = cv2.LINE_AA)


buttonHelper = ButtonHelper()