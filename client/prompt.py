import pyautogui
import os 
def alertPrompt(text):
    pyautogui.alert(text)

def inputPrompt(text):
    value = pyautogui.prompt(text," : ")
    pc_name = os.environ["USERNAME"]
    return pc_name+" : Recieved = "+value