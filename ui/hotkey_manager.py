from typing import Callable
from global_hotkeys import *
import threading
import time

class HotkeyManager:
    def __init__(self, on_activate: Callable):
        self.on_activate = on_activate
        self.is_alive = True
        
        # Define hotkey binding
        bindings = [
            ["alt + shift + F8", None, self._on_hotkey, False]  # False = don't actuate on partial release
        ]
        
        # Start listener in a separate thread
        thread = threading.Thread(target=self._start_listener, args=(bindings,))
        thread.daemon = True
        thread.start()

    def _on_hotkey(self):
        """Handle hotkey activation"""
        self.on_activate()

    def _start_listener(self, bindings):
        """Start the hotkey listener"""
        try:
            # Register hotkeys
            register_hotkeys(bindings)
            
            # Start listening
            start_checking_hotkeys()
            
            # Keep thread alive
            while self.is_alive:
                time.sleep(0.1)
        except Exception as e:
            print(f"Hotkey error (non-critical): {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the hotkey listener"""
        self.is_alive = False
        try:
            stop_checking_hotkeys()
        except:
            pass  # Ignore errors during shutdown
