import tkinter as tk
from tkinter import ttk
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
from .window_relations_manager import WindowRelationsManager
import pyautogui
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class SearchWindow:
    def __init__(self, on_search: Callable, on_action: Callable, on_select: Callable, 
                 on_connect: Callable, on_get_recent_entries: Callable):
        # Create root window
        self.root = tk.Tk()
        
        # Initialize keyboard controller
        self.keyboard = Controller()
        
        # Track last hotkey activation time
        self.last_hotkey_time = 0  # Initialize to 0 (epoch time)
        
        # Initialize window relations manager
        self.window_relations_manager = WindowRelationsManager()
        
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
            DarkEntry,
            self._handle_enter_action,
            self._handle_highlight_change,
            self._handle_action_highlight_change,
            self.show_initial_view
        )
        self.results = ResultsView(self.window.get_main_frame())
        self.actions = None
        # Store callbacks
        self.on_search = on_search
        self.on_action = on_action
        self.on_select = on_select
        self.on_connect = on_connect  # Callback for lazy database connection
        self.on_get_recent_entries = on_get_recent_entries  # Callback for getting recent entries
        
        # Bind events
        self.root.bind('<Return>', self._handle_return)
        self.root.bind('<Escape>', lambda e: self.hide())
        self.root.bind('<FocusOut>', self.window.check_focus)
        
        # Start hotkey listener
        self.hotkey = HotkeyManager(self.show_window)

    def _handle_search(self, search_term: str):
        """Handle search request"""
        print(f"SearchWindow._handle_search called with term: '{search_term}'")
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
        
        # Log the entry selection
        try:
            self.window_relations_manager.log_entry_selection(entry)
        except Exception as e:
            print(f"Error logging entry selection: {e}")
            
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
        elif action == 'auto_type':
            # Auto type username and password
            self.hide()
            self.root.after(1000, self._type_credentials, entry.username, entry.password)
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
        print("Handling reset request")
        print(f"Entries count: {len(self.input.entries) if self.input.entries else 0}")
        print(f"Current input mode before reset: {self.input.current_mode}")
        
        # Clear results and actions
        self.results.clear()
        if self.actions:
            self.actions.hide()
            self.actions = None

        # Check if we have entries to show
        if self.input.entries and len(self.input.entries) > 0:
            print(f"Showing {len(self.input.entries)} entries")
            # Show the entries
            self.results.show_entries(self.input.entries)
            self.window.set_expanded(True)
            self.status.set_text("Recent entries for this window:")
            
            # Make sure the entries are visible
            self.results.frame.pack(fill=tk.BOTH, expand=True)
        else:
            print("No entries to show")
            self.window.set_expanded(False)
            self.status.set_text("")
            
        print(f"Current input mode after reset: {self.input.current_mode}")

    def _handle_return(self, event):
        """Handle Return key"""
        # If we're in action mode, perform the action for the highlighted button
        if self.input.current_mode == InputMode.ACTION and self.input.current_entry and self.actions:
            # Get the currently highlighted action
            current_index = self.actions.get_current_highlight()
            if current_index >= 0 and current_index < self.actions.get_action_count():
                # Get the action name from the button
                action = self.actions.buttons[current_index]["action"]
                # Handle the action
                self._handle_action(action, self.input.current_entry)
                return "break"
        return self.input.handle_return()
        
    def _handle_enter_action(self, entry):
        """Handle Enter key in action mode - auto-fill username and password"""
        # Hide the window first
        self.hide()
        
        # Schedule the typing operation with a delay
        self.root.after(1000, self._type_credentials, entry.username, entry.password)
        
    def _type_credentials(self, username: str, password: str):
        """Type username, tab, password, enter sequence"""
        # Type username
        self._type_text(username)
        
        # Press Tab
        time.sleep(0.1)
        self.keyboard.press(Key.tab)
        self.keyboard.release(Key.tab)
        time.sleep(0.1)
        
        # Type password
        self._type_text(password)
        
        # Press Enter
        time.sleep(0.1)
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)

    def show_window(self):
        """Show the window"""
        # Log active window title before showing the window
        try:
            self.window_relations_manager.log_active_window()
        except Exception as e:
            print(f"Error logging active window: {e}")
            
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
            
            # Check for recent entries for this window
            recent_entry_ids = self.window_relations_manager.get_recent_entries_for_current_window()
            if recent_entry_ids:
                # Get entries from KeePass database
                recent_entries = self.on_get_recent_entries(recent_entry_ids)
                if recent_entries:
                    # Show recent entries
                    self.show_recent_entries(recent_entries)
            else:
                # No recent entries, just show search
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
        
    def show_recent_entries(self, entries):
        """Show recent entries for the current window"""
        if not entries:
            return
            
        print(f"Showing {len(entries)} recent entries")
            
        # Display a header for recent entries
        self.status.set_text("Recent entries for this window:")
        
        # Show entries in the results view and keep search input active
        self.show_entries(entries, keep_search_mode=True)
        
        print(f"Current input mode: {self.input.current_mode}")
        
    def show_initial_view(self):
        """Show the initial view with recent entries for the current window"""
        # Reset to main search
        self._handle_reset()
        
        # Check for recent entries for this window
        recent_entry_ids = self.window_relations_manager.get_recent_entries_for_current_window()
        if recent_entry_ids:
            # Get entries from KeePass database
            recent_entries = self.on_get_recent_entries(recent_entry_ids)
            if recent_entries:
                # Show recent entries
                self.show_recent_entries(recent_entries)
        else:
            # No recent entries, just show search
            self.input.show_search()
        
        # Clear the search input
        self.input.set_search_text("")
    
    def _ensure_focus(self):
        """Ensure the current input has focus"""
        print(f"_ensure_focus called, current mode: {self.input.current_mode}")
        if self.input.current_mode == InputMode.SEARCH:
            print("Focusing search input")
            self.input.search_input.focus_force()
        elif self.input.current_mode == InputMode.LIST:
            print("Focusing list input")
            self.input.list_input.focus_force()
        elif self.input.current_mode == InputMode.ACTION:
            print("Focusing action input")
            self.input.action_input.focus_force()

    def hide(self):
        """Hide the window"""
        #if self.actions:
            #self.actions.hide()  # Just hide the buttons, don't destroy them
        self.window.hide()

    def _handle_highlight_change(self, direction: str):
        """Handle highlight change in results view"""
        current_index = self.results.get_current_highlight()
        entry_count = self.results.get_entry_count()
        
        if entry_count == 0:
            return
            
        # Special case: if on first entry and pressing up, deselect all entries
        if direction == 'up' and current_index == 0:
            # Clear highlight and reset current entry
            self.results.current_highlight = -1
            self.input.current_entry = None
            
            # Clear any highlighted entries in the UI
            for i in range(len(self.results.entry_frames)):
                frame = self.results.entry_frames[i]['frame']
                frame.configure(style='Dark.TFrame')
                
                # Change style of all child labels
                for child in frame.winfo_children():
                    if isinstance(child, ttk.Label):
                        # Check if it's a URL label (smaller font)
                        if child.cget('font') == ('Segoe UI', 10):
                            child.configure(style='Dark.TLabel')
                        else:
                            child.configure(style='Dark.TLabel')
            
            # Ensure focus is on the search input
            self.input.search_input.focus_force()
            return
            
        # Calculate new index based on direction
        if direction == 'up':
            new_index = max(0, current_index - 1) if current_index >= 0 else entry_count - 1
        elif direction == 'down':
            new_index = (current_index + 1) % entry_count if current_index >= 0 else 0
        else:
            return
            
        # Highlight the new entry and update current_entry
        entry = self.results.highlight_entry(new_index)
        if entry:
            self.input.current_entry = entry
            
        # Ensure the window is expanded to show results
        self.window.set_expanded(True)
            
    def _handle_action_highlight_change(self, direction: str):
        """Handle highlight change in action buttons"""
        if not self.actions:
            return
            
        # Use the ActionButtons' highlight change handler
        self.actions.handle_highlight_change(direction)
            
    def show_entries(self, entries: List[Any], keep_search_mode=True):
        """Show search results"""
        print(f"show_entries called with {len(entries)} entries, keep_search_mode={keep_search_mode}")
        # Clear previous results
        self.results.clear()
        if self.actions:
            self.actions.hide()
            self.actions = None  # Destroy actions when showing new entries
        
        if not entries:
            self.window.set_expanded(False)
            self.status.set_text("No entries found")
            return
            
        if len(entries) == 1 and not keep_search_mode:
            # Single entry - show actions directly
            entry = entries[0]
            self.window.set_expanded(True)
            self.status.show_search_results(entries, entry)
            # Set the entry in InputManager before showing actions
            print("Single entry, showing actions")
            self.input.show_list(entries)  # This will set current_entry and call show_actions
            #self.actions.show()
            self.actions = ActionButtons(self.window.get_main_frame(), lambda action: self._handle_action(action, entry), self.input.get_current_entry())
            self.actions.show()
        
        else:
            # Multiple entries or keep_search_mode is True
            self.window.set_expanded(True)
            self.results.show_entries(entries)
            self.status.show_search_results(entries)
            
            if keep_search_mode:
                # Store entries but keep search input active
                print("keep_search_mode is True, keeping search input active")
                self.input.entries = entries.copy()
                # Don't highlight any entry by default
                self.input.current_entry = None
                self.results.current_highlight = -1
                # Ensure we're in search mode
                self.input.show_search()
            else:
                # Show list mode
                print("keep_search_mode is False, showing list mode")
                self.input.show_list(entries)
                
                # Highlight the first entry by default
                if entries:
                    entry = self.results.highlight_entry(0)
                    if entry:
                        self.input.current_entry = entry

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
