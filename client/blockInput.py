from pynput import keyboard, mouse
import threading

# Global flags and listener references
keyboard_block = True
mouse_block = True
pressed_keys = set()
kb_listener = None
mouse_listener = None
#

def unblock_all():
    """Unblock keyboard and mouse by stopping listeners."""
    global keyboard_block, mouse_block, kb_listener, mouse_listener
    keyboard_block = False
    mouse_block = False

    if kb_listener:
        kb_listener.stop()
        kb_listener = None
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None

    print("Keyboard and mouse unblocked!")

def block_keyboard():
    """Keyboard blocking listener."""
    global pressed_keys, kb_listener
    pressed_keys = set()

    def on_press(key):
        pressed_keys.add(key)

        # Check unblock combination first
        try:
            chars = [k.char for k in pressed_keys if hasattr(k, 'char')]
        except:
            chars = []

        ctrl = keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys
        shift = keyboard.Key.shift in pressed_keys

        if ctrl and shift and 'a' in chars and 'v' in chars:
            unblock_all()  # stop both threads

        if keyboard_block:
            return True  # suppress keys

    def on_release(key):
        if key in pressed_keys:
            pressed_keys.remove(key)

    kb_listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True)
    kb_listener.start()

def block_mouse():
    """Mouse blocking listener."""
    global mouse_listener

    def on_click(x, y, button, pressed):
        if not mouse_block:
            return False  # stop listener
        return mouse_block  # suppress clicks if blocking

    mouse_listener = mouse.Listener(on_click=on_click, suppress=True)
    mouse_listener.start()

def start_block(target="both"):
    """Start blocking keyboard and/or mouse."""
    threads = []
    if target in ["keyboard", "both"]:
        t1 = threading.Thread(target=block_keyboard)
        threads.append(t1)
        t1.start()
    if target in ["mouse", "both"]:
        t2 = threading.Thread(target=block_mouse)
        threads.append(t2)
        t2.start()
    return threads
