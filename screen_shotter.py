import pyautogui
import pygetwindow as gw
from PIL import ImageGrab

import cv2 as cv
import numpy as np
from time import time
from mss import mss
from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionAll
import Quartz

def get_window_dimensions(hwnd):
    window_info_list = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionIncludingWindow, hwnd)
    for window_info in window_info_list:
        window_id = window_info[Quartz.kCGWindowNumber]
        if window_id == hwnd:
            bounds = window_info[Quartz.kCGWindowBounds]
            width = bounds['Width']
            height = bounds['Height']
            left = bounds['X']
            top = bounds['Y']
            return {"top": top, "left": left, "width": width, "height": height}
    return None


def window_capture(window_name, image_path="screenshot.png"):
    loop_time = time()
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in window_list:
        # print(window.get('kCGWindowName', ''))
        if window_name.lower() == window.get('kCGWindowName', '').lower():
            hwnd = window['kCGWindowNumber']
            print('found window id %s' % hwnd)
    monitor = get_window_dimensions(hwnd)
    with mss() as sct:
        screenshot = np.array(sct.grab(monitor))
        # screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
        # cv.imshow('Computer Vision', screenshot)
        # resize the image
        # screenshot = cv.resize(screenshot, (342//2, 758//2))
        # save the image
        cv.imwrite(image_path, screenshot)

if __name__ == "__main__":
    window_name = "iPhone Mirroring"
    window_capture(window_name=window_name)