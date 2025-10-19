import ctypes
import time
import os
import json 
def display_off():
    ctypes.windll.user32.SendMessageW(0xFFFF,0x112,0xF170,2)

def display_on():
    ctypes.windll.user32.mouse_event(1,0,0,0,0)

import ctypes
import pyautogui
import time

class SYSTEM_VOLUME:
    @staticmethod
    def get_volume():
        devices = ctypes.windll.winmm
        vol = ctypes.c_uint()
        devices.waveOutGetVolume(0, ctypes.byref(vol))
        return vol.value & 0xFFFF

def mute_volume():
    if SYSTEM_VOLUME.get_volume() > 0:
        pyautogui.press('volumemute')

def full_volume():
    while SYSTEM_VOLUME.get_volume() < 65535:
        pyautogui.press('volumeup')
        time.sleep(0.005)



