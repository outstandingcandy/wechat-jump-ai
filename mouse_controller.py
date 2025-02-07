import pyautogui
import time

def move_mouse(x, y):
    pyautogui.moveTo(x, y)

def click_mouse():
    pyautogui.click()

def press_and_hold_mouse(t):
    pyautogui.mouseDown()
    time.sleep(t)
    pyautogui.mouseUp()

if __name__ == "__main__":
    move_mouse(100, 100)
    press_and_hold_mouse(2)  # Press and hold the mouse button for 2 seconds