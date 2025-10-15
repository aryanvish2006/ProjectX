import threading
import pyautogui
import os

def alertPrompt(text):
    threading.Thread(target=pyautogui.alert, args=(text,)).start()

def inputPrompt(text):
    def prompt_thread():
        value = pyautogui.prompt(text, " : ")
        pc_name = os.environ["USERNAME"]
        print(pc_name + " : Received = " + str(value))
    threading.Thread(target=prompt_thread).start()
