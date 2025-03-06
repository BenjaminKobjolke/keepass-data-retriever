import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Type
from enum import Enum, auto

class InputMode(Enum):
    SEARCH = auto()
    LIST = auto()
    ACTION = auto()

class InputManager:
    def __init__(self, parent: ttk.Frame, on_search: Callable, on_select: Callable, 
                 on_action: Callable, on_escape: Callable, on_reset: Callable, 
                 entry_class: Type[ttk.Entry], on_enter_action: Callable = None):
        self.on_search = on_search
        self.on_select = on_select
        self.on_action = on_action
        self.on_escape = on_escape
        self.on_reset = on_reset
        self.on_enter_action = on_enter_action
        
        # Create input frame to position all inputs
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.frame.pack(padx=2, pady=2)
        
        # Create search entry
        self.search_input = entry_class(self.frame, width=40)
        self.search_input.grid(row=0, column=0)
        
        # Create list selection input
        self.list_input = entry_class(self.frame, width=40)
        self.list_input.grid(row=0, column=0)
        self.list_input.grid_remove()  # Hide initially
        
        # Create action selection input
        self.action_input = entry_class(self.frame, width=40)
        self.action_input.grid(row=0, column=0)
        self.action_input.grid_remove()  # Hide initially
        
        # Bind events
        self.search_input.bind('<Return>', self._handle_search)
        self.list_input.bind('<Key>', self._handle_list_key)
        self.action_input.bind('<Key>', self._handle_action_key)
        self.action_input.bind('<Return>', self._handle_action_return)
        
        # Bind ESC key to all inputs
        self.search_input.bind('<Escape>', self._handle_escape)
        self.list_input.bind('<Escape>', self._handle_escape)
        self.action_input.bind('<Escape>', self._handle_escape)
        
        self.entries = []  # Store entries for list selection
        self.current_entry = None  # Store single entry for action mode
        self.current_mode = InputMode.SEARCH

    def _handle_escape(self, event):
        """Handle ESC key"""
        self.on_escape()
        return "break"

    def _handle_search(self, event):
        """Handle search entry Return key"""
        search_term = self.search_input.get()
        self.on_search(search_term)
        return "break"

    def _handle_list_key(self, event):
        """Handle key press in list selection input"""
        print(f"List key pressed: {event.char}, keysym: {event.keysym}")
        
        # Handle Backspace key to go back to main GUI
        if event.keysym == 'BackSpace':
            self.reset_to_search()  # Reset state and go back to search
            return "break"
            
        if event.char == '0':
            self.reset_to_search()  # Reset state and go back to search
        elif event.char.isdigit():
            number = int(event.char)
            if number <= len(self.entries):
                selected_entry = self.entries[number - 1]
                self.current_entry = selected_entry  # Store the selected entry
                self.on_select(selected_entry)
        
        # Clear the input
        self.list_input.delete(0, tk.END)
        return "break"

    def _handle_action_key(self, event):
        """Handle key press in action selection input"""
        print(f"Action key pressed: {event.char}, keysym: {event.keysym}")
        
        # Handle Backspace key to go back to main GUI
        if event.keysym == 'BackSpace':
            self.reset_to_search()  # Reset state and go back to search
            return "break"
            
        if event.char == '0':
            self.reset_to_search()  # Reset state and go back to search
        elif event.char.isdigit():
            number = int(event.char)
            if 1 <= number <= 6:  # Now handling 6 actions
                actions = [
                    'username',      # 1: Copy Username
                    'password',      # 2: Copy Password
                    'type_username', # 3: Paste Username
                    'type_password',  # 4: Paste Password
                    'url',          # 5: Copy URL
                    'open_url',      # 6: Open URL
                                        
                ]
                self.on_action(actions[number - 1], self.current_entry)
                # Hide window after any action
                self.on_escape()
        
        # Clear the input
        self.action_input.delete(0, tk.END)
        return "break"

    def reset_to_search(self):
        """Reset state and return to search input"""
        self.entries = []
        self.current_entry = None
        self.on_reset()  # Call reset callback to clear results
        self.show_search()

    def show_search(self):
        """Show search input"""
        self.list_input.grid_remove()
        self.action_input.grid_remove()
        self.search_input.grid()
        self.search_input.focus_force()
        self.search_input.select_range(0, tk.END)
        self.current_mode = InputMode.SEARCH

    def show_list(self, entries):
        """Show list selection input"""
        self.entries = entries
        
        # If only one entry, go straight to action mode
        if len(entries) == 1:
            self.current_entry = entries[0]
            self.show_actions()
            return
            
        self.current_entry = None
        self.search_input.grid_remove()
        self.action_input.grid_remove()
        self.list_input.grid()
        self.list_input.focus_force()
        self.current_mode = InputMode.LIST
        print("Moving focus to list input")

    def show_actions(self):
        """Show action selection input"""
        self.search_input.grid_remove()
        self.list_input.grid_remove()
        self.action_input.grid()
        self.action_input.focus_force()
        self.current_mode = InputMode.ACTION
        print("Moving focus to action input")

    def restore_last_mode(self):
        """Restore the last active input mode"""
        if self.current_mode == InputMode.SEARCH:
            self.show_search()
        elif self.current_mode == InputMode.LIST and self.entries:
            self.show_list(self.entries)
        elif self.current_mode == InputMode.ACTION:
            self.show_actions()
        else:
            self.show_search()  # Default to search if no valid state

    def set_search_text(self, text: str):
        """Set the search input text"""
        self.search_input.delete(0, tk.END)
        self.search_input.insert(0, text)

    def _handle_action_return(self, event):
        """Handle Return key in action input"""
        print("Action Return key pressed")
        if self.current_entry and self.on_enter_action:
            self.on_enter_action(self.current_entry)
            return "break"
        return False
        
    def handle_return(self):
        """Handle Return key to reactivate search"""
        if self.search_input != self.search_input.focus_get():
            self.show_search()
            return True
        return False

    def get_current_entry(self):
        """Get the current entry"""
        return self.current_entry
