import ctypes
import time
import os
import json 
def display_off():
    ctypes.windll.user32.SendMessageW(0xFFFF,0x112,0xF170,2)

def display_on():
    ctypes.windll.user32.mouse_event(1,0,0,0,0)



