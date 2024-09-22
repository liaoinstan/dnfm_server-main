from config import FRAME_WIDTH

DEVICE_WIDTH: int
DEVICE_HEIGHT: int
RATE: float = 0.45
SCALE: float = 0

HEROS = {}
CURRENT_HERO = None

def setDeviceResolution(width: int, height: int):
    global DEVICE_WIDTH, DEVICE_HEIGHT, RATE, SCALE
    DEVICE_WIDTH = width
    DEVICE_HEIGHT = height
    RATE = DEVICE_HEIGHT/DEVICE_WIDTH
    if FRAME_WIDTH != 0:
        SCALE = FRAME_WIDTH/DEVICE_WIDTH
    else:
        SCALE = 1


def log():
    global DEVICE_WIDTH, DEVICE_HEIGHT, RATE, SCALE
    print(f"手机分辨率:{DEVICE_HEIGHT}*{DEVICE_WIDTH}, RATE:{RATE}, SCALE:{SCALE}")
