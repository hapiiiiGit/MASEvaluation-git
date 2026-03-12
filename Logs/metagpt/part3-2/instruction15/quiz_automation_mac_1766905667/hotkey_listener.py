import threading
from typing import Callable, Optional
from pynput import keyboard


class HotkeyListener:
    """
    Listens for a customizable hotkey and triggers the provided callback.
    Uses pynput for cross-platform hotkey listening (macOS compatible).
    """

    def __init__(self, hotkey: str, callback: Callable):
        """
        Initializes the hotkey listener.
        Args:
            hotkey: Hotkey string, e.g., 'cmd+shift+o'
            callback: Function to call when hotkey is pressed
        """
        self.hotkey = hotkey.lower()
        self.callback = callback
        self.listener: Optional[keyboard.Listener] = None
        self._stop_event = threading.Event()
        self._hotkey_set = self._parse_hotkey(self.hotkey)
        self._pressed_keys = set()

    def _parse_hotkey(self, hotkey_str: str):
        """
        Parses the hotkey string into a set of pynput key objects.
        Supports 'cmd', 'ctrl', 'alt', 'shift', and single character keys.
        """
        key_map = {
            'cmd': keyboard.Key.cmd,
            'command': keyboard.Key.cmd,
            'ctrl': keyboard.Key.ctrl,
            'control': keyboard.Key.ctrl,
            'alt': keyboard.Key.alt,
            'option': keyboard.Key.alt,
            'shift': keyboard.Key.shift,
        }
        keys = set()
        for part in hotkey_str.split('+'):
            part = part.strip()
            if part in key_map:
                keys.add(key_map[part])
            elif len(part) == 1:
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                raise ValueError(f"Unsupported hotkey part: {part}")
        return keys

    def _on_press(self, key):
        self._pressed_keys.add(key)
        if self._hotkey_set.issubset(self._pressed_keys):
            # Hotkey pressed
            self.callback()

    def _on_release(self, key):
        if key in self._pressed_keys:
            self._pressed_keys.remove(key)

    def start_listening(self) -> None:
        """
        Starts listening for the hotkey in a non-blocking thread.
        """
        self._stop_event.clear()
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        print(f"[INFO] Hotkey listener started. Waiting for hotkey: {self.hotkey}")

    def stop_listening(self) -> None:
        """
        Stops listening for the hotkey.
        """
        self._stop_event.set()
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        print("[INFO] Hotkey listener stopped.")


if __name__ == "__main__":
    # Example usage: listen for Cmd+Shift+O and print a message
    def test_callback():
        print("[HOTKEY] Hotkey pressed! Triggering automation...")

    hotkey = "cmd+shift+o"
    listener = HotkeyListener(hotkey, test_callback)
    listener.start_listening()

    try:
        while True:
            pass  # Keep main thread alive
    except KeyboardInterrupt:
        listener.stop_listening()
        print("Exiting hotkey listener.")