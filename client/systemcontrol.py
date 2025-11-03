import ctypes
import pyautogui
import time
import requests
import os
import tempfile
import psutil
import shlex
def display_off():
    ctypes.windll.user32.SendMessageW(0xFFFF,0x112,0xF170,2)

def display_on():
    ctypes.windll.user32.mouse_event(1,0,0,0,0)

def full_volume():
    for _ in range(50):
        pyautogui.press('volumeup')
        time.sleep(0.01)  

def mute_volume():
    for _ in range(50):
        pyautogui.press('volumedown')
        time.sleep(0.01)


def set_wallpaper_from_url(url: str):
    """Downloads an image from the given URL, sets it as wallpaper, then deletes it."""
    try:
        # Temporary file path (universal)
        temp_dir = tempfile.gettempdir()
        img_path = os.path.join(temp_dir, "temp_wallpaper.jpg")

        # Download image
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        with open(img_path, "wb") as f:
            f.write(response.content)

        # Apply wallpaper
        ctypes.windll.user32.SystemParametersInfoW(20, 0, img_path, 3)
        return("🖼️ Wallpaper applied successfully.")

    except Exception as e:
        return(f"❌ Error: {e}")
    finally:
        # Clean up the downloaded file
        if os.path.exists(img_path):
            os.remove(img_path)
            return("🧹 Temporary image deleted.")


def run_psutil_from_string(cmd_str: str):
    """
    Runs psutil commands from a single string.
    Examples:
      "cpu_percent interval=1"
      "disk_usage C:\\"
      "virtual_memory"
    """
    try:
        parts = shlex.split(cmd_str)  # split safely, supports quoted args
        if not parts:
            return {"error": "Empty command"}

        command = parts[0]
        args = []
        kwargs = {}

        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                # Try to convert to int/float/bool if possible
                if v.isdigit():
                    v = int(v)
                elif v.replace('.', '', 1).isdigit():
                    v = float(v)
                elif v.lower() in ("true", "false"):
                    v = v.lower() == "true"
                kwargs[k] = v
            else:
                args.append(p)

        if not hasattr(psutil, command):
            return {"error": f"No such psutil function: {command}"}

        func = getattr(psutil, command)
        if not callable(func):
            return {"error": f"{command} is not callable"}

        result = func(*args, **kwargs)

        def convert(obj):
            if hasattr(obj, "_asdict"):
                return obj._asdict()
            elif isinstance(obj, (list, tuple)):
                return [convert(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            else:
                return obj

        return {"function": command, "result": convert(result)}

    except Exception as e:
        return {"error": str(e)}

user32 = ctypes.windll.user32

def get_open_and_active_windows():
    open_windows = []

    def enum_windows_callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.strip()
                if title:
                    open_windows.append(title)
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)

    # Get active (foreground) window
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    active_window = buff.value.strip()

    return {
        "active_window": active_window,
        "open_windows": open_windows
    }