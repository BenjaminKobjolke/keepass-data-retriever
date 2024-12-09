import tkinter as tk
from tkinter import ttk
from typing import Callable
import time
from pynput.keyboard import Controller
from .dark_button import DarkButton
import pyautogui

class ActionButtons:
    def __init__(self, parent: ttk.Frame, on_action: Callable, entry=None):
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.on_action = on_action
        self.keyboard = Controller()
        self.current_entry = None
        self._create_buttons(entry)

    def _create_buttons(self, entry=None):
        """Create action buttons"""
        actions = [
            ("Copy username (1)", "username"),
            ("Copy password (2)", "password")
        ]
        actions += [
            ("Type username (3)", "type_username"),
            ("Type password (4)", "type_password")
        ]

        if entry and entry.url:
            actions.append(("Copy URL (5)", "url"))
            actions.append(("Open URL (6)", "open_url"))
        

        
        for text, action in actions:
            btn = DarkButton(
                self.frame,
                text=text,
                command=lambda a=action: self._handle_action(a),
                width=30  # Make buttons wider
            )
            btn.pack(fill=tk.X, pady=2)  # Slightly more vertical spacing

    def _handle_action(self, action: str):
        """Handle button actions"""
        if not self.current_entry:
            print("No entry selected")
            return
        
        print("Entry ", self.current_entry)
            
        if action.startswith('type_'):
            # For paste actions, get the text first
            base_action = action.replace('type_', '')
            #self.on_action(base_action, self.current_entry)  # Pass the entry along
            
            # Schedule the paste operation
            self.frame.after(1000, lambda: self._paste_text())
        else:
            # Normal copy/open actions
            self.on_action(action, self.current_entry)  # Pass the entry along

    def _paste_text(self):
        """Type the clipboard content"""
        with self.keyboard.pressed(self.keyboard.ctrl_key):
            self.keyboard.press('v')
            self.keyboard.release('v')

    def show(self, entry=None):
        """Show action buttons"""
        self.current_entry = entry
        self.frame.pack(fill=tk.X, padx=5, pady=5)

    def hide(self):
        """Hide action buttons"""
        self.current_entry = None
        self.frame.pack_forget()
