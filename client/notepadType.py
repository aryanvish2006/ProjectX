import time
import pyautogui as pg
import random
import threading

def notepad_write(text,drawHeart):
    pg.press("win")
    time.sleep(1)
    pg.typewrite("notepad",0.3)
    time.sleep(2.5)
    pg.press("enter")
    time.sleep(2)
    pg.hotkey("alt","space","x")
    time.sleep(.3)
    for _ in range(15):
        pg.hotkey("ctrl","=")
        time.sleep(0.05)
    time.sleep(0.2)    
    pg.typewrite(text,0.3)
    time.sleep(3)
    pg.hotkey("alt","f4")
    time.sleep(1)
    pg.press("right")
    time.sleep(.5)
    pg.press("enter")

move_flag = False
screen_width,screen_height = pg.size()
def random_move():
    global move_flag
    while move_flag:
        x=random.randint(100,screen_width-100)
        y=random.randint(100,screen_height-100)
        pg.moveTo(x,y,0.2)
        time.sleep(0.3)     
def start_random_move():
    global move_flag
    if not move_flag:
        move_flag= True
        threading.Thread(target=random_move,daemon=True).start()
def stop_random_move():
    global move_flag
    move_flag=False        