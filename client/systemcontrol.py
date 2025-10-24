import ctypes
import pyautogui
import time

def display_off():
    ctypes.windll.user32.SendMessageW(0xFFFF,0x112,0xF170,2)

def display_on():
    ctypes.windll.user32.mouse_event(1,0,0,0,0)

def full_volume():
    for _ in range(50):
        pyautogui.press('volumeup')
        time.sleep(0.01)  

def mute_volume():
    for _ in range(50):
        pyautogui.press('volumedown')
        time.sleep(0.01)




