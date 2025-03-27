import time
from pynput.keyboard import Controller, Key
from typing import Any
from .logger import Logger

# Get logger instance
logger = Logger.get_instance()

class KeyboardHandler:
    """Handles keyboard input and typing operations"""
    
    def __init__(self):
        """Initialize the keyboard controller"""
        self.keyboard = Controller()
    
    def type_text(self, text: str):
        """Type the text character by character"""
        logger.debug(f"Typing text: {text[:3]}...")  # Log only first few characters for privacy
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
