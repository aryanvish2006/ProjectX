import tkinter as tk
import math
import time
import pyautogui as pg


def notepad_write(text,drawHeart):
    pg.press("win")
    time.sleep(1)
    pg.typewrite("notepad",0.3)
    time.sleep(1.5)
    pg.press("enter")
    time.sleep(1.5)
    pg.hotkey("alt","space","x")
    time.sleep(.5)
    pg.typewrite(text,0.3)

    if drawHeart:
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.attributes('-transparentcolor', 'white')
        root.overrideredirect(True)

        canvas = tk.Canvas(root, width=500, height=500, bg='white', highlightthickness=0)
        canvas.pack()

        def heart(t, scale=10, offset=(250, 250)):
            x = scale * 16 * math.sin(t)**3
            y = -scale * (13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t))
            return x + offset[0], y + offset[1]

        for i in range(0, 628):
            t = i / 100
            x, y = heart(t)
            canvas.create_oval(x, y, x+2, y+2, fill='red', outline='red')
            root.update()       # Refresh window to show the new point
            time.sleep(0.01)    # Small delay for live drawing effect

    time.sleep(3)
    pg.hotkey("alt","f4")
    time.sleep(1)
    pg.press("right")
    time.sleep(.5)
    pg.press("enter")
    if drawHeart:
        root.destroy()