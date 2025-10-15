from pynput import keyboard, mouse
import threading

# ------------------ Global flags ------------------
keyboard_block = True
mouse_block = True
pressed_keys = set()
kb_listener = None
mouse_listener = None

# ------------------ Unblock function ------------------
def unblock_all():
    """Stop all listeners and unblock input."""
    global keyboard_block, mouse_block, kb_listener, mouse_listener
    keyboard_block = False
    mouse_block = False

    if kb_listener:
        kb_listener.stop()
        kb_listener = None
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None

    print("[INFO] Keyboard and mouse unblocked!")

# ------------------ Keyboard blocking ------------------
def block_keyboard():
    """Start keyboard blocking listener in a non-blocking way."""
    global pressed_keys, kb_listener
    pressed_keys = set()

    def on_press(key):
        pressed_keys.add(key)

        # Detect unblock combination: Ctrl + Shift + A + V
        try:
            chars = [k.char for k in pressed_keys if hasattr(k, 'char')]
        except:
            chars = []

        ctrl = keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys
        shift = keyboard.Key.shift in pressed_keys

        if ctrl and shift and 'a' in chars and 'v' in chars:
            unblock_all()

        # If still blocking, suppress keys
        if keyboard_block:
            return False  # suppress key

    def on_release(key):
        if key in pressed_keys:
            pressed_keys.remove(key)

    kb_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release,
        suppress=True  # blocks keys from reaching system
    )
    kb_listener.start()  # non-blocking

# ------------------ Mouse blocking ------------------
def block_mouse():
    """Start mouse blocking listener in a non-blocking way."""
    global mouse_listener

    def on_click(x, y, button, pressed):
        if not mouse_block:
            return False  # stop listener
        return mouse_block  # suppress click if blocking

    mouse_listener = mouse.Listener(on_click=on_click, suppress=True)
    mouse_listener.start()  # non-blocking

# ------------------ Start blocking ------------------
def start_block(target="both"):
    """Start blocking keyboard/mouse without freezing main loop."""
    if target in ["keyboard", "both"]:
        threading.Thread(target=block_keyboard, daemon=True).start()
    if target in ["mouse", "both"]:
        threading.Thread(target=block_mouse, daemon=True).start()

# ------------------ Example usage ------------------
if __name__ == "__main__":
    print("[INFO] Blocking keyboard and mouse. Use Ctrl+Shift+A+V to unblock.")
    start_block("both")

    # Main loop continues running
    count = 0
    while True:
        print(f"Main loop running... {count}")
        count += 1
        import time
        time.sleep(1)
