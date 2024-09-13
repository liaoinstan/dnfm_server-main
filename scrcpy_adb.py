
import cv2
from adbutils import adb
import time
import scrcpy
from config import WINDOW_WIDTH, RATE


class ScrcpyADB:
    def __init__(self, image_queue, max_fps=15):
        devices = adb.device_list()
        client = scrcpy.Client(device=devices[0], max_width=WINDOW_WIDTH, max_fps=max_fps, block_frame=True)
        print(devices, client)
        client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
        client.start(threaded=True)
        self.client = client
        self.last_screen = None
        self.frame_idx = -1
        self.queue = image_queue

    def touch_down(self, x: int or float, y: int or float, id: int = -1):
        x, y = convetPoint(x, y)
        # print("xxxx touch_down:", x, y)
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_DOWN, id)

    def touch_move(self, x: int or float, y: int or float, id: int = -1):
        x, y = convetPoint(x, y)
        # print("xxxx touch_move:", x, y)
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_MOVE, id)

    def touch_up(self, x: int or float, y: int or float, id: int = -1):
        x, y = convetPoint(x, y)
        # print("xxxx touch_up:", x, y)
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_UP, id)

    def touch_swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        move_step_length: int = 5,
        move_steps_delay: float = 0.005,
    ):
        start_x, start_y = convetPoint(start_x, start_y)
        end_x, end_y = convetPoint(end_x, end_y)
        self.client.control.swipe(start_x, start_y, end_x, end_y, move_step_length, move_steps_delay)

    def tap(self, x: int or float, y: int or float):
        self.touch_start(x, y)
        time.sleep(0.01)
        self.touch_end(x, y)

    def on_frame(self, frame: cv2.Mat):

        if frame is not None:
            self.queue.put(frame)

def convetPoint(x, y):
    return x*RATE, y*RATE


if __name__ == '__main__':
    client = ScrcpyADB(None, max_fps=15)
    time.sleep(1)
    client.touch_down(200, 200)
    client.touch_move(300, 300)
    client.touch_up(300, 300)
