
import cv2
from adbutils import adb
import time
import scrcpy
from config import WINDOW_WIDTH
import subprocess
import re
from BWJRoomHelperV2 import roomHelper


class ScrcpyADB:
    def __init__(self, image_queue, max_fps=15):
        # 获取adb设备列表
        devices = adb.device_list()
        # 取第一台为游戏设备
        if WINDOW_WIDTH == 0:
            client = scrcpy.Client(device=devices[0], max_fps=max_fps, block_frame=True)
        else:
            client = scrcpy.Client(device=devices[0], max_width=WINDOW_WIDTH, max_fps=max_fps, block_frame=True)
        print(devices, client)
        # 发送adb命令获取物理屏幕分辨率
        process = subprocess.Popen("adb shell wm size", shell=True, stdout=subprocess.PIPE)
        output, error = process.communicate()
        if output:
            # 正则解析返回结果
            print(output.decode())
            result = re.search(r'\d{4}x(\d{4})', output.decode())
            # 初始化
            if WINDOW_WIDTH == 0:
                self.rate = 1
            else:
                self.rate = WINDOW_WIDTH/int(result.group(1))
            roomHelper.init(self.rate)
        if error:
            print("设备异常:", error.decode())
            return
        # 添加数据流回调
        client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
        # 启动scrcpy
        client.start(threaded=True)
        self.client = client
        self.last_screen = None
        self.frame_idx = -1
        self.queue = image_queue

    def convetPoint(self, x, y):
        return x*self.rate, y*self.rate

    def touch_down(self, x: int or float, y: int or float, id: int = -1):
        x, y = self.convetPoint(x, y)
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_DOWN, id)

    def touch_move(self, x: int or float, y: int or float, id: int = -1):
        x, y = self.convetPoint(x, y)
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_MOVE, id)

    def touch_up(self, x: int or float, y: int or float, id: int = -1):
        x, y = self.convetPoint(x, y)
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
        start_x, start_y = self.convetPoint(start_x, start_y)
        end_x, end_y = self.convetPoint(end_x, end_y)
        self.client.control.swipe(start_x, start_y, end_x, end_y, move_step_length, move_steps_delay)

    def tap(self, x: int or float, y: int or float):
        self.touch_start(x, y)
        time.sleep(0.01)
        self.touch_end(x, y)

    def on_frame(self, frame: cv2.Mat):
        if frame is not None:
            self.queue.put(frame)


if __name__ == '__main__':
    client = ScrcpyADB(None, max_fps=15)
    time.sleep(1)
    client.touch_down(200, 200)
    client.touch_move(300, 300)
    client.touch_up(300, 300)
