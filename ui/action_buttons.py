import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any
import time
from pynput.keyboard import Controller
from .dark_button import DarkButton
from .state_manager import StateManager, AppState
from .logger import Logger
from .theme_manager import ThemeManager
from .action_registry import ActionRegistry
from config import config
import pyautogui

# Get logger instance
logger = Logger.get_instance()

class ActionButtons:
    @property
    def HIGHLIGHT_BG(self):
        return ThemeManager.get_color('action_highlight_bg')

    @property
    def NORMAL_BG(self):
        return ThemeManager.get_color('button_bg')

    def __init__(self, parent: ttk.Frame, on_action: Callable, entry=None, state_manager: StateManager = None):
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.on_action = on_action
        self.keyboard = Controller()
        self.current_entry = entry
        self.buttons = []     # Store buttons for highlighting
        self.current_highlight = -1  # Currently highlighted button
        self.state_manager = state_manager
        
        self._create_buttons(entry)
        
        # Register as state listener if state manager is provided
        if self.state_manager:
            self.state_manager.register_listener(self)
    
    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"ActionButtons: State changed to {state}")
        
        if state == AppState.ENTRY_ACTIONS:
            # Show action buttons for the selected entry
            entry = data.get('entry')
            if entry and entry != self.current_entry:
                self.current_entry = entry
                self._create_buttons(entry)  # Recreate buttons with the new entry
                self.show()
        elif state == AppState.INITIAL or state == AppState.SEARCH or state == AppState.RESULTS_LIST or state == AppState.HIDDEN:
            # Hide action buttons for other states
            self.hide()

    def _create_buttons(self, entry=None):
        """Create action buttons"""
        # Destroy any existing buttons
        for child in self.frame.winfo_children():
            child.destroy()

        # Get paste mode setting
        paste_mode = config.get_paste_mode()

        # Get available actions based on whether entry has URL
        has_url = entry and entry.url
        actions = ActionRegistry.get_all_actions(has_url=has_url)

        self.buttons = []  # Clear buttons list

        button_width = max(20, int(config.get_window_width() / 14))

        for i, action_def in enumerate(actions):
            label = ActionRegistry.get_label(action_def['id'], paste_mode=paste_mode)
            btn = DarkButton(
                self.frame,
                text=label,
                command=lambda a=action_def['id']: self._handle_action(a),
                width=button_width
            )
            btn.pack(fill=tk.X, pady=2)  # Slightly more vertical spacing
            self.buttons.append({"button": btn, "action": action_def['id'], "index": i})

    def _handle_action(self, action: str):
        """Handle button actions"""
        if not self.current_entry:
            logger.warning("No entry selected")
            return
        
        logger.debug(f"Entry: {self.current_entry}")
            
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
        if entry:
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

        # Unregister from state manager
        if self.state_manager:
            self.state_manager.unregister_listener(self)
