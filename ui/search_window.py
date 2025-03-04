import tkinter as tk
from typing import Optional, Callable, List, Any
import time
from pynput.keyboard import Controller, Key
from .window_manager import WindowManager
from .input_manager import InputManager, InputMode
from .status_display import StatusDisplay
from .results_view import ResultsView
from .action_buttons import ActionButtons
from .hotkey_manager import HotkeyManager
from .dark_entry import DarkEntry
import pyautogui
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class SearchWindow:
    def __init__(self, on_search: Callable, on_action: Callable, on_select: Callable, on_connect: Callable):
        # Create root window
        self.root = tk.Tk()
        
        # Initialize keyboard controller
        self.keyboard = Controller()
        
        # Track last hotkey activation time
        self.last_hotkey_time = 0  # Initialize to 0 (epoch time)
        
        # Initialize components
        self.window = WindowManager(self.root)
        self.status = StatusDisplay(self.window.get_main_frame())
        self.input = InputManager(
            self.window.get_main_frame(),
            self._handle_search,
            self._handle_select,
            self._handle_action,
            self.hide,
            self._handle_reset,
            DarkEntry
        )
        self.results = ResultsView(self.window.get_main_frame())
        self.actions = None
        # Store callbacks
        self.on_search = on_search
        self.on_action = on_action
        self.on_select = on_select
        self.on_connect = on_connect  # New callback for lazy database connection
        
        # Bind events
        self.root.bind('<Return>', self._handle_return)
        self.root.bind('<Escape>', lambda e: self.hide())
        self.root.bind('<FocusOut>', self.window.check_focus)
        
        # Start hotkey listener
        self.hotkey = HotkeyManager(self.show_window)

    def _handle_search(self, search_term: str):
        """Handle search request"""
        self.on_search(search_term)

    def _handle_select(self, entry: Any):
        """Handle entry selection"""
        self.actions = ActionButtons(self.window.get_main_frame(), lambda action: self._handle_action(action, entry), self.input.get_current_entry())        
        self.on_select(entry)

    def _handle_action(self, action: str, entry: Any = None):
        """Handle action request"""
        if not entry:
            print("No entry selected")
            return
        print("action is ", action)
        if action.startswith('type_'):
            # For paste actions, get the text first
            base_action = action.replace('type_', '')
            # Hide window first
            self.hide()
            # Schedule the paste operation
            text_to_type = entry.username
            if base_action == 'password':
                text_to_type = entry.password
            self.root.after(1000, self._type_text, text_to_type)
        else:
            # Normal copy/open actions
            self.on_action(action, entry)  # Pass the entry along
            self.hide()

    def _type_text(self, text: str):
        """Type the text"""
        for character in text:
            self.keyboard.press(character)
            self.keyboard.release(character)
            time.sleep(0.01)  # Small delay between keystrokes

    def _paste_text(self):
        """Type the clipboard content"""
        with self.keyboard.pressed(Key.ctrl):
            self.keyboard.press('v')
            self.keyboard.release('v')

    def _handle_reset(self):
        """Handle reset request"""
        self.results.clear()
        if self.actions:
            self.actions.hide()
            self.actions = None

        self.window.set_expanded(False)
        self.status.set_text("")

    def _handle_return(self, event):
        """Handle Return key"""
        return self.input.handle_return()

    def show_window(self):
        """Show the window"""
        # First check if we need to connect to the database
        if not self.on_connect():
            # Connection failed or was cancelled, don't show window
            return
            
        current_time = time.time()
        
        # Show the window first
        self.window.show()
        
        # Check if more than the configured time has passed since last activation
        search_reset_timeout = config.get_search_reset_timeout()
        if current_time - self.last_hotkey_time > search_reset_timeout:
            # Reset to main search
            self._handle_reset()
            self.input.show_search()
            # Clear the search input
            self.input.set_search_text("")
        else:
            # Restore last mode as before
            self.input.restore_last_mode()
        
        # Update last hotkey time
        self.last_hotkey_time = current_time
        
        # Schedule an additional focus call after a short delay
        self.root.after(100, self._ensure_focus)
    
    def _ensure_focus(self):
        """Ensure the current input has focus"""
        if self.input.current_mode == InputMode.SEARCH:
            self.input.search_input.focus_force()
        elif self.input.current_mode == InputMode.LIST:
            self.input.list_input.focus_force()
        elif self.input.current_mode == InputMode.ACTION:
            self.input.action_input.focus_force()

    def hide(self):
        """Hide the window"""
        #if self.actions:
            #self.actions.hide()  # Just hide the buttons, don't destroy them
        self.window.hide()

    def show_entries(self, entries: List[Any]):
        """Show search results"""
        # Clear previous results
        self.results.clear()
        if self.actions:
            self.actions.hide()
            self.actions = None  # Destroy actions when showing new entries
        
        if not entries:
            self.window.set_expanded(False)
            self.status.set_text("No entries found")
            return
            
        if len(entries) == 1:
            # Single entry - show actions directly
            entry = entries[0]
            self.window.set_expanded(True)
            self.status.show_search_results(entries, entry)
            # Set the entry in InputManager before showing actions
            self.input.show_list(entries)  # This will set current_entry and call show_actions
            #self.actions.show()
            self.actions = ActionButtons(self.window.get_main_frame(), lambda action: self._handle_action(action, entry), self.input.get_current_entry())
            self.actions.show()
        
        else:
            # Multiple entries - show list
            self.window.set_expanded(True)
            self.results.show_entries(entries)
            self.status.show_search_results(entries)
            self.input.show_list(entries)

    def show_selected_entry(self, entry: Any):
        """Show selected entry"""
        self.results.clear()
        self.status.show_selected_entry(entry)
        # Ensure InputManager has the current entry before showing actions
        self.input.current_entry = entry
        self.input.show_actions()
        self.actions.show()

    def set_search_text(self, text: str):
        """Set the search input text"""
        self.input.set_search_text(text)

    def set_status(self, text: str):
        """Set status text"""
        self.status.set_text(text)

    def run(self):
        """Start the application"""
        hotkey = config.get_search_hotkey()
        print(f"KeePass Search running. Press {hotkey} to open search window.")
        print("Right-click the window for menu options.")
        self.root.mainloop()
