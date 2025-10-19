import pyautogui

def alertPrompt(text):
    pyautogui.alert(text)

def inputPrompt(text):
    value = pyautogui.prompt(text, " : ")
    return "Received = " + str(value) 