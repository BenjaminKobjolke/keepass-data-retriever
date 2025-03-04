from typing import Callable
from global_hotkeys import *
import threading
import time
import sys
import os
import re

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class HotkeyManager:
    # Default hotkey to use if the configured one fails
    DEFAULT_HOTKEY = "alt + shift + F8"
    
    # List of supported modifier keys
    SUPPORTED_MODIFIERS = ["alt", "ctrl", "shift"]
    
    # Mapping for modifier keys that need translation
    MODIFIER_MAPPING = {
        "ctrl": "control"
    }
    
    def __init__(self, on_activate: Callable):
        self.on_activate = on_activate
        self.is_alive = True
        
        # Get hotkey from config
        configured_hotkey = config.get_search_hotkey()
        
        # Validate and normalize the hotkey
        hotkey, is_valid = self._validate_and_translate_hotkey(configured_hotkey)
        
        if not is_valid:
            print(f"Warning: Invalid hotkey format '{configured_hotkey}'. Using default: {self.DEFAULT_HOTKEY}")
            hotkey = self.DEFAULT_HOTKEY
        
        # Define hotkey binding
        bindings = [
            [hotkey, None, self._on_hotkey, False]  # False = don't actuate on partial release
        ]
        
        # Start listener in a separate thread
        thread = threading.Thread(target=self._start_listener, args=(bindings,))
        thread.daemon = True
        thread.start()

    def _on_hotkey(self):
        """Handle hotkey activation"""
        self.on_activate()

    def _validate_and_translate_hotkey(self, hotkey_str):
        """
        Validate and normalize the hotkey string.
        
        Args:
            hotkey_str: The hotkey string from config
            
        Returns:
            tuple: (normalized_hotkey, is_valid)
        """
        # Check if the string is empty
        if not hotkey_str or not isinstance(hotkey_str, str):
            return self.DEFAULT_HOTKEY, False
        
        # Normalize the string: lowercase, remove extra spaces
        normalized = hotkey_str.lower().strip()
        
        # Split by '+' and strip each part
        parts = [part.strip() for part in normalized.split('+')]
        
        # Translate modifiers if needed
        translated_parts = []
        for part in parts:
            if part in self.MODIFIER_MAPPING:
                translated_parts.append(self.MODIFIER_MAPPING[part])
            else:
                translated_parts.append(part)
        
        # Reconstruct the hotkey string
        translated_hotkey = ' + '.join(translated_parts)
        
        # Check if we have at least one modifier and one key
        if len(parts) < 2:
            return self.DEFAULT_HOTKEY, False
        
        # Check if the last part is a function key or letter
        last_part = parts[-1]
        if not (re.match(r'^f\d+$', last_part) or len(last_part) == 1):
            return self.DEFAULT_HOTKEY, False
        
        # Check if all modifiers are supported
        modifiers = parts[:-1]
        for modifier in modifiers:
            if modifier not in self.SUPPORTED_MODIFIERS and modifier != "win":
                return self.DEFAULT_HOTKEY, False
        
        # Special handling for 'win' key - it's not directly supported
        if "win" in modifiers:
            print("Warning: 'win' key is not supported by the global_hotkeys package.")
            return self.DEFAULT_HOTKEY, False
        
        return translated_hotkey, True

    def _start_listener(self, bindings):
        """Start the hotkey listener"""
        try:
            # Register hotkeys
            print(f"Registering hotkey: {bindings[0][0]}")
            register_hotkeys(bindings)
            
            # Start listening
            start_checking_hotkeys()
            
            # Keep thread alive
            while self.is_alive:
                time.sleep(0.1)
        except Exception as e:
            print(f"Hotkey registration error: {e}")
            print("Falling back to default hotkey...")
            
            try:
                # Try with default hotkey
                clear_hotkeys()
                fallback_bindings = [
                    [self.DEFAULT_HOTKEY, None, self._on_hotkey, False]
                ]
                register_hotkeys(fallback_bindings)
                start_checking_hotkeys()
                
                print(f"Successfully registered fallback hotkey: {self.DEFAULT_HOTKEY}")
                
                # Keep thread alive
                while self.is_alive:
                    time.sleep(0.1)
            except Exception as e2:
                print(f"Critical error registering fallback hotkey: {e2}")
        finally:
            self.stop()

    def stop(self):
        """Stop the hotkey listener"""
        self.is_alive = False
        try:
            stop_checking_hotkeys()
        except:
            pass  # Ignore errors during shutdown
