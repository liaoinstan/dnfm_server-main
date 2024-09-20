import os

import cv2
import numpy as np
import time


def match_template(large_image, template_image_path, threshold=0.8):
    """
    在大图中查找模板图，并返回是否匹配成功以及匹配区域的中心点坐标。

    参数:
    large_image_path: str, 大图的文件路径
    template_image_path: str, 模板图的文件路径
    threshold: float, 匹配的阈值，默认为0.8

    返回:
    is_matched: bool, 是否匹配成功
    center_coordinates: tuple, 匹配区域的中心点坐标 (x, y) 或 None（如果未匹配成功）
    elapsed_time: float, 匹配过程耗时（单位：秒）
    """

    # 读取大图和模板图

    template_image = cv2.imread(template_image_path)

    if large_image is None or template_image is None:
        raise ValueError("无法读取图片，请检查图片路径是否正确。")

    # 获取模板图的宽度和高度
    w, h = template_image.shape[1], template_image.shape[0]

    # 使用模板匹配方法查找匹配位置
    result = cv2.matchTemplate(large_image, template_image, cv2.TM_CCOEFF_NORMED)

    # 找到大于阈值的位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 判断是否匹配成功
    if max_val >= threshold:
        # 计算匹配区域的中心点坐标
        top_left = max_loc
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        center_coordinates = (center_x, center_y)
        return True, center_coordinates
    else:
        return False, None

def __toFullPath(relativePath: str)-> str:
    parent_directory = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir))
    parent_directory = os.path.dirname(parent_directory)
    return os.path.abspath(f'{parent_directory}/template/{relativePath}')

def match_again(imgPath):
    """
        匹配再来一次：
    """
    is_matched, center_coordinates = match_template(__toFullPath('again/again_button.png'), imgPath)
    return is_matched, center_coordinates


def match_start(imgPath):
    """
        委托按钮：
    """
    is_matched, center_coordinates = match_template(__toFullPath('way_to_bwj/entrust_button.png'), imgPath)
    return is_matched, center_coordinates


def match_map(imgPath):
    """
        山脊地图选择界面：
    """
    is_matched, center_coordinates = match_template(__toFullPath('way_to_bwj/sj_button.png'), imgPath)
    return is_matched
