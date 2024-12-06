import threading
from typing import Callable
from pynput import keyboard

class HotkeyManager:
    def __init__(self, on_activate: Callable):
        self.on_activate = on_activate
        self.listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        self.listener_thread.start()

    def _start_listener(self):
        """Start listening for Alt+Shift+R hotkey"""
        def for_canonical(f):
            return lambda k: f(self.listener.canonical(k))
            
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<alt>+<shift>+r'),
            self.on_activate
        )
        
        with keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        ) as self.listener:
            self.listener.join()
