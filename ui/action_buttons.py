import tkinter as tk
from tkinter import ttk
from typing import Callable
import time
from pynput.keyboard import Controller
from .dark_button import DarkButton
import pyautogui

class ActionButtons:
    # Define colors for highlighting
    HIGHLIGHT_BG = '#5a5a5a'  # Much lighter than background for better visibility
    NORMAL_BG = '#3d3d3d'     # Default button background
    
    def __init__(self, parent: ttk.Frame, on_action: Callable, entry=None):
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.on_action = on_action
        self.keyboard = Controller()
        self.current_entry = None
        self.buttons = []     # Store buttons for highlighting
        self.current_highlight = -1  # Currently highlighted button
        self._create_buttons(entry)

    def _create_buttons(self, entry=None):
        """Create action buttons"""
        # Start with Auto type as the first action
        actions = [
            ("Auto type (1)", "auto_type")
        ]
        
        # Add other actions with updated numbering
        actions += [
            ("Copy username (2)", "username"),
            ("Copy password (3)", "password"),
            ("Type username (4)", "type_username"),
            ("Type password (5)", "type_password")
        ]

        if entry and entry.url:
            actions.append(("Copy URL (6)", "url"))
            actions.append(("Open URL (7)", "open_url"))
        
        self.buttons = []  # Clear buttons list
        
        for i, (text, action) in enumerate(actions):
            btn = DarkButton(
                self.frame,
                text=text,
                command=lambda a=action: self._handle_action(a),
                width=30  # Make buttons wider
            )
            btn.pack(fill=tk.X, pady=2)  # Slightly more vertical spacing
            self.buttons.append({"button": btn, "action": action, "index": i})

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

    def highlight_action(self, index: int) -> str:
        """Highlight the action at the given index and return the action name"""
        if not self.buttons or index < 0 or index >= len(self.buttons):
            return None
            
        # Clear previous highlight if any
        if self.current_highlight >= 0 and self.current_highlight < len(self.buttons):
            prev_button = self.buttons[self.current_highlight]["button"]
            prev_button.configure(background=self.NORMAL_BG)
        
        # Set new highlight
        self.current_highlight = index
        current_button = self.buttons[index]["button"]
        current_button.configure(background=self.HIGHLIGHT_BG)
                
        # Return the action name
        return self.buttons[index]["action"]
        
    def handle_highlight_change(self, direction: str) -> str:
        """Handle highlight change and return the highlighted action"""
        button_count = len(self.buttons)
        
        if button_count == 0:
            return None
            
        # Calculate new index based on direction
        if direction == 'up':
            new_index = max(0, self.current_highlight - 1) if self.current_highlight >= 0 else button_count - 1
        elif direction == 'down':
            new_index = (self.current_highlight + 1) % button_count if self.current_highlight >= 0 else 0
        else:
            return None
            
        # Highlight the new action
        return self.highlight_action(new_index)
        
    def get_current_highlight(self) -> int:
        """Get the index of the currently highlighted action"""
        return self.current_highlight
        
    def get_action_count(self) -> int:
        """Get the number of actions"""
        return len(self.buttons)
        
    def show(self, entry=None):
        """Show action buttons"""
        self.current_entry = entry
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Highlight the first action by default
        if self.buttons:
            self.highlight_action(0)

    def hide(self):
        """Hide action buttons"""
        self.current_entry = None
        self.frame.pack_forget()
        # Reset highlight when hiding
        self.current_highlight = -1
