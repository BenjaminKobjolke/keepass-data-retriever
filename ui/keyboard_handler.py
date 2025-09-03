import time
from pynput.keyboard import Controller, Key
from typing import Any
import pyperclip
from .logger import Logger
from config import config

# Get logger instance
logger = Logger.get_instance()

class KeyboardHandler:
    """Handles keyboard input and typing operations"""
    
    def __init__(self):
        """Initialize the keyboard controller"""
        self.keyboard = Controller()
        self.paste_mode = config.get_paste_mode()
    
    def type_text(self, text: str):
        """Type text using either paste mode or typing mode based on configuration"""
        logger.debug(f"{'Pasting' if self.paste_mode else 'Typing'} text: {text[:3]}...")  # Log only first few characters for privacy
        
        # Determine whether to use paste mode
        use_paste = self.paste_mode or ('^' in text)
        
        if use_paste:
            logger.debug("Using clipboard paste method")
            # Copy text to clipboard
            pyperclip.copy(text)
            time.sleep(0.1)  # Delay to ensure clipboard is fully updated
            # Paste using Ctrl+V
            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press('v')
                self.keyboard.release('v')
            time.sleep(0.05)  # Small delay after paste for stability
        else:
            logger.debug("Using character-by-character typing")
            # Use the original character-by-character typing
            for character in text:
                self.keyboard.press(character)
                self.keyboard.release(character)
                time.sleep(0.01)  # Small delay between keystrokes

    def paste_text(self):
        """Type the clipboard content using Ctrl+V"""
        logger.debug("Pasting text from clipboard")
        with self.keyboard.pressed(Key.ctrl):
            self.keyboard.press('v')
            self.keyboard.release('v')

    def type_credentials(self, username: str, password: str):
        """Type username, tab, password, enter sequence"""
        logger.debug("Typing credentials sequence")
        # Type username
        self.type_text(username)
        
        # Press Tab
        time.sleep(0.1)
        self.keyboard.press(Key.tab)
        self.keyboard.release(Key.tab)
        time.sleep(0.1)
        
        # Type password
        self.type_text(password)
        
        # Press Enter
        time.sleep(0.1)
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
