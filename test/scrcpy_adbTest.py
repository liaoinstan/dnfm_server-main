
import cv2
from adbutils import adb
import time
import scrcpy
from BWJRoomHelper import roomHelper
import numpy as np

windowWidth = 800
deviceWidth = 3200


class ScrcpyADB:
    def __init__(self, max_fps=15):
        devices = adb.device_list()
        client = scrcpy.Client(device=devices[0],max_width=windowWidth,  max_fps=max_fps)
        print(devices, client)
        client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
        client.start(threaded=True)
        self.client = client
        self.last_screen = None

    def on_frame(self, frame: cv2.Mat):

        if frame is not None:
            self.last_screen = frame
            # print("xxx shape:",frame.shape)
            # 640,288,3
            # 3200,1440,3
            # self.queue.put(frame)
            # pass
            # room = calcuRoomNum(frame)
            # print("room",room)

def convetPoint(x, y):
    rate = windowWidth/deviceWidth
    return x*rate, y*rate

if __name__ == '__main__':
    sadb = ScrcpyADB()
    while True:
        # time.sleep(0.1)
        if sadb.last_screen is None:
            continue
        
        # sadb.last_screen = np.rot90(sadb.last_screen, k=1)

        roomNum = roomHelper.parseRoomNum(sadb.last_screen)
        if roomNum == 5:
            print("roomNum",str(roomNum) + " (狮子头)")
        elif roomNum == 8:
            print("roomNum",str(roomNum) + " (BOSS)")
        else:
            print("roomNum",roomNum)

        cv2.imshow('screen', sadb.last_screen)
        # cv.waitKey(1)
        key = cv2.waitKey(1)
        if key == ord('q'):  # 检查用户是否按下了"q"
            cv2.destroyAllWindows()
            sadb.client.stop()
            break
