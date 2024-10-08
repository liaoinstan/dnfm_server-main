
import cv2
from adbutils import adb
import time
import datetime
import scrcpy
from config import FRAME_WIDTH
import re
from component.utils.BWJRoomHelperV2 import roomHelper
import component.utils.RuntimeData as R
import os
import threading

# def globalExceptionHandler(exctype, value, traceback):
#     # 处理未被捕获的异常
#     print("An unhandled exception occurred:")
#     print(f"Exception type: {exctype}")
#     print(f"Exception value: {value}")
#     print(f"Traceback: {traceback}")

# sys.excepthook = globalExceptionHandler


class ScrcpyADB:
    def __init__(self, image_queue, onConnect, onDisconnect, max_fps=15):
        self.queue = image_queue
        self.max_fps = max_fps
        self.onConnect = onConnect
        self.onDisconnect = onDisconnect
        self.connectThread: ConnectThread = None
        self.lastFrame = None
        self.client = None
        self.init()

    def init(self):
        # 获取adb设备列表
        devices = adb.device_list()
        if len(devices) == 0:
            print("未找到设备")
            if self.connectThread is None or self.connectThread.running == False:
                self.connectThread = ConnectThread(self.init)
                self.connectThread.start()
            return
        if self.connectThread:
            self.connectThread.stop()
        # 取第一台为游戏设备
        if FRAME_WIDTH == 0:
            client = scrcpy.Client(device=devices[0], max_fps=self.max_fps, block_frame=True)
        else:
            client = scrcpy.Client(device=devices[0], max_width=FRAME_WIDTH, max_fps=self.max_fps, block_frame=True)
        self.onConnect()
        print(devices, client)
        # 发送adb命令获取物理屏幕分辨率
        output = client.device.shell("wm size")
        if output:
            # 正则解析返回结果
            print("手机分辨率", output)
            result = re.search(r'(\d+)x(\d+)', output)
            # 初始化
            R.setDeviceResolution(int(result.group(2)), int(result.group(1)))
            R.log()
            roomHelper.init()
        else:
            print("设备异常，请检查设备连接状态")
            return
        # 添加数据流回调
        client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
        client.add_listener(scrcpy.EVENT_DISCONNECT, self.on_disconnect)
        # 启动scrcpy
        client.start(threaded=True)
        self.client = client
        self.last_screen = None
        self.frame_idx = -1

    def stop(self):
        if self.client:
            self.client.stop()
        if self.connectThread:
            self.connectThread.stop()

    def convetPoint(self, x, y):
        return x*R.SCALE, y*R.SCALE

    def touch_down(self, x: int or float, y: int or float, id: int = -1, convert=True):
        if convert:
            x, y = self.convetPoint(x, y)
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_DOWN, id)

    def touch_move(self, x: int or float, y: int or float, id: int = -1, convert=True):
        if convert:
            x, y = self.convetPoint(x, y)
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_MOVE, id)

    def touch_up(self, x: int or float, y: int or float, id: int = -1, convert=True):
        if convert:
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
        convert=True
    ):
        if convert:
            start_x, start_y = self.convetPoint(start_x, start_y)
            end_x, end_y = self.convetPoint(end_x, end_y)
        self.client.control.swipe(start_x, start_y, end_x, end_y, move_step_length, move_steps_delay)

    def tap(self, x: int or float, y: int or float, convert=True):
        if convert:
            x, y = self.convetPoint(x, y)
        self.touch_start(x, y)
        time.sleep(0.01)
        self.touch_end(x, y)

    def on_frame(self, frame: cv2.Mat):
        if frame is not None:
            self.lastFrame = frame
            self.queue.put(frame)

    def screenshot(self):
        folder_name = "screenshort"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        currentTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
        fileName = f'screenshot_{currentTime}.jpg'
        cv2.imwrite(f'{folder_name}/{fileName}', self.lastFrame)
        print(f"已生成截图: {fileName}")

    def on_disconnect(self):
        print("设备已断连")
        self.onDisconnect()
        self.connectThread = ConnectThread(self.init)
        self.connectThread.start()


class ConnectThread(threading.Thread):
    def __init__(self, callback):
        super().__init__(name="ConnectThread")
        self.callback = callback
        self.running = False

    def run(self):
        print(f"Thread {self.name} started")
        while self.running:
            self.callback()
            time.sleep(1)
        print(f"Thread {self.name} finished")

    def stop(self):
        self.running = False

    def start(self):
        self.running = True
        super().start()


if __name__ == '__main__':
    client = ScrcpyADB(None, max_fps=15)
    time.sleep(1)
    client.touch_down(200, 200)
    client.touch_move(300, 300)
    client.touch_up(300, 300)
