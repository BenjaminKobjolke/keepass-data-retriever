import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from enum import Enum, auto

class InputMode(Enum):
    SEARCH = auto()
    LIST = auto()
    ACTION = auto()

class InputManager:
    def __init__(self, parent: ttk.Frame, on_search: Callable, on_select: Callable, on_action: Callable, on_escape: Callable, on_reset: Callable):
        self.on_search = on_search
        self.on_select = on_select
        self.on_action = on_action
        self.on_escape = on_escape
        self.on_reset = on_reset
        
        # Create input frame to position all inputs
        self.frame = ttk.Frame(parent)
        self.frame.pack(padx=5, pady=5)
        
        # Create search entry
        self.search_input = ttk.Entry(self.frame, width=30)
        self.search_input.grid(row=0, column=0)
        
        # Create list selection input
        self.list_input = ttk.Entry(self.frame, width=30)
        self.list_input.grid(row=0, column=0)
        self.list_input.grid_remove()  # Hide initially
        
        # Create action selection input
        self.action_input = ttk.Entry(self.frame, width=30)
        self.action_input.grid(row=0, column=0)
        self.action_input.grid_remove()  # Hide initially
        
        # Bind events
        self.search_input.bind('<Return>', self._handle_search)
        self.list_input.bind('<Key>', self._handle_list_key)
        self.action_input.bind('<Key>', self._handle_action_key)
        
        # Bind ESC key to all inputs
        self.search_input.bind('<Escape>', self._handle_escape)
        self.list_input.bind('<Escape>', self._handle_escape)
        self.action_input.bind('<Escape>', self._handle_escape)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TEntry', padding='5')
        
        self.entries = []  # Store entries for list selection
        self.single_entry = None  # Store single entry for action mode
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
        print(f"List key pressed: {event.char}")
        if event.char == '0':
            self.reset_to_search()  # Reset state and go back to search
        elif event.char.isdigit():
            number = int(event.char)
            if number <= len(self.entries):
                self.on_select(self.entries[number - 1])
        
        # Clear the input
        self.list_input.delete(0, tk.END)
        return "break"

    def _handle_action_key(self, event):
        """Handle key press in action selection input"""
        print(f"Action key pressed: {event.char}")
        if event.char == '0':
            self.reset_to_search()  # Reset state and go back to search
        elif event.char.isdigit():
            number = int(event.char)
            if 1 <= number <= 4:
                actions = ['username', 'password', 'url', 'open_url']
                self.on_action(actions[number - 1])
        
        # Clear the input
        self.action_input.delete(0, tk.END)
        return "break"

    def reset_to_search(self):
        """Reset state and return to search input"""
        self.entries = []
        self.single_entry = None
        self.on_reset()  # Call reset callback to clear results
        self.show_search()

    def _ensure_focus(self, widget: ttk.Entry):
        """Ensure the widget has focus"""
        self.frame.after(10, lambda: widget.focus_force())

    def show_search(self):
        """Show search input"""
        self.list_input.grid_remove()
        self.action_input.grid_remove()
        self.search_input.grid()
        self.search_input.select_range(0, tk.END)
        self.current_mode = InputMode.SEARCH
        self._ensure_focus(self.search_input)

    def show_list(self, entries):
        """Show list selection input"""
        self.entries = entries
        
        # If only one entry, go straight to action mode
        if len(entries) == 1:
            self.single_entry = entries[0]
            self.show_actions()
            return
            
        self.single_entry = None
        self.search_input.grid_remove()
        self.action_input.grid_remove()
        self.list_input.grid()
        self.current_mode = InputMode.LIST
        self._ensure_focus(self.list_input)
        print("Moving focus to list input")

    def show_actions(self):
        """Show action selection input"""
        self.search_input.grid_remove()
        self.list_input.grid_remove()
        self.action_input.grid()
        self.current_mode = InputMode.ACTION
        self._ensure_focus(self.action_input)
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

    def handle_return(self):
        """Handle Return key to reactivate search"""
        if self.search_input != self.search_input.focus_get():
            self.show_search()
            return True
        return False
