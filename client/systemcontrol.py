import ctypes
import pyautogui
import time
import requests
import os
import tempfile
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
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(img_path, "wb") as f:
            f.write(response.content)

        # Apply wallpaper
        ctypes.windll.user32.SystemParametersInfoW(20, 0, img_path, 3)
        print("🖼️ Wallpaper applied successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up the downloaded file
        if os.path.exists(img_path):
            os.remove(img_path)
            print("🧹 Temporary image deleted.")
       


