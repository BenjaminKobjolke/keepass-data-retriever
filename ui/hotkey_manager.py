from typing import Callable, Optional
import tkinter as tk

# Import directly from the winhotkeys library
try:
    from winhotkeys import HotkeyHandler
except ImportError:
    # If that fails, try a direct import from the local file
    from hotkey import HotkeyHandler
import sys
import os
import re

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config
from .logger import Logger

logger = Logger.get_instance()


class HotkeyManager:
    # Default hotkey to use if the configured one fails
    DEFAULT_HOTKEY = "alt+ctrl+F8"

    # List of supported modifier keys
    SUPPORTED_MODIFIERS = ["alt", "ctrl", "shift"]

    # Mapping for modifier keys that need translation
    MODIFIER_MAPPING = {"ctrl": "control"}

    def __init__(self, on_activate: Callable, root: Optional[tk.Tk] = None):
        self.on_activate = on_activate
        self.root = root

        # Get hotkey from config
        configured_hotkey = config.get_search_hotkey()

        # Validate and normalize the hotkey
        hotkey, is_valid = self._validate_and_translate_hotkey(configured_hotkey)

        if not is_valid:
            logger.warning(
                f"Warning: Invalid hotkey format '{configured_hotkey}'. Using default: {self.DEFAULT_HOTKEY}"
            )
            hotkey = self.DEFAULT_HOTKEY

        try:
            # Create hotkey handler
            logger.info(f"Registering hotkey: {hotkey}")
            self.hotkey_handler = HotkeyHandler(hotkey, self._on_hotkey, suppress=True)

            # Start listening
            self.hotkey_handler.start()
        except Exception as e:
            logger.error(f"Hotkey registration error: {e}")
            logger.info("Falling back to default hotkey...")

            try:
                # Try with default hotkey
                self.hotkey_handler = HotkeyHandler(
                    self.DEFAULT_HOTKEY, self._on_hotkey, suppress=True
                )
                self.hotkey_handler.start()
                logger.info(f"Successfully registered fallback hotkey: {self.DEFAULT_HOTKEY}")
            except Exception as e2:
                logger.error(f"Critical error registering fallback hotkey: {e2}")
                self.hotkey_handler = None

    def _on_hotkey(self):
        """Handle hotkey activation.

        winhotkeys fires this on its keyboard hook thread. Marshal onto the
        Tk main thread via root.after so all UI work runs on the right thread.
        Hook thread holds the brief foreground privilege from WM_HOTKEY; the
        main thread does not, so SetForegroundWindow would fail there. Grant
        our own process explicit permission before marshalling.
        """
        try:
            import ctypes

            ctypes.windll.user32.AllowSetForegroundWindow(os.getpid())
        except Exception:
            pass

        if self.root is not None:
            try:
                self.root.after(0, self.on_activate)
            except tk.TclError:
                pass  # Root being torn down during shutdown
        else:
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
        parts = [part.strip() for part in normalized.split("+")]

        # Translate modifiers if needed
        translated_parts = []
        for part in parts:
            if part in self.MODIFIER_MAPPING:
                translated_parts.append(self.MODIFIER_MAPPING[part])
            else:
                translated_parts.append(part)

        # Reconstruct the hotkey string - winhotkeys uses format without spaces
        translated_hotkey = "+".join(translated_parts)

        # Check if we have at least one modifier and one key
        if len(parts) < 2:
            return self.DEFAULT_HOTKEY, False

        # Check if the last part is a function key or letter
        last_part = parts[-1]
        if not (re.match(r"^f\d+$", last_part) or len(last_part) == 1):
            return self.DEFAULT_HOTKEY, False

        # Check if all modifiers are supported
        modifiers = parts[:-1]
        for modifier in modifiers:
            if modifier not in self.SUPPORTED_MODIFIERS and modifier != "win":
                return self.DEFAULT_HOTKEY, False

        # Special handling for 'win' key - check if it's supported by winhotkeys
        if "win" in modifiers:
            logger.warning("Warning: 'win' key might not be fully supported.")

        return translated_hotkey, True

    def stop(self):
        """Stop the hotkey listener"""
        if hasattr(self, "hotkey_handler") and self.hotkey_handler:
            try:
                self.hotkey_handler.stop()
            except Exception:
                pass  # Ignore errors during shutdown
