import tkinter as tk
from typing import Optional, Callable, List, Any
from .window_manager import WindowManager
from .input_manager import InputManager
from .status_display import StatusDisplay
from .results_view import ResultsView
from .action_buttons import ActionButtons
from .hotkey_manager import HotkeyManager

class SearchWindow:
    def __init__(self, on_search: Callable, on_action: Callable, on_select: Callable):
        # Create root window
        self.root = tk.Tk()
        
        # Initialize components
        self.window = WindowManager(self.root)
        self.status = StatusDisplay(self.window.get_main_frame())
        self.input = InputManager(
            self.window.get_main_frame(),
            self._handle_search,
            self._handle_select,
            self._handle_action,
            self.hide,
            self._handle_reset  # Add reset handler
        )
        self.results = ResultsView(self.window.get_main_frame())
        self.actions = ActionButtons(self.window.get_main_frame(), on_action)
        
        # Store callbacks
        self.on_search = on_search
        self.on_action = on_action
        self.on_select = on_select
        
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
        self.on_select(entry)

    def _handle_action(self, action: str):
        """Handle action request"""
        self.on_action(action)
        self.hide()

    def _handle_reset(self):
        """Handle reset request"""
        self.results.clear()
        self.actions.hide()
        self.window.set_expanded(False)
        self.status.set_text("")

    def _handle_return(self, event):
        """Handle Return key"""
        return self.input.handle_return()

    def show_window(self):
        """Show the window"""
        self.window.show()
        self.input.restore_last_mode()

    def hide(self):
        """Hide the window"""
        self.window.hide()

    def show_entries(self, entries: List[Any]):
        """Show search results"""
        # Clear previous results
        self.results.clear()
        self.actions.hide()
        
        if not entries:
            self.window.set_expanded(False)
            self.status.set_text("No entries found")
            return
            
        if len(entries) == 1:
            # Single entry - show actions directly
            self.window.set_expanded(True)
            self.status.show_search_results(entries, entries[0])
            self.actions.show()
            self.input.show_actions()
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
        self.actions.show()
        self.input.show_actions()

    def set_search_text(self, text: str):
        """Set the search input text"""
        self.input.set_search_text(text)

    def set_status(self, text: str):
        """Set status text"""
        self.status.set_text(text)

    def run(self):
        """Start the application"""
        print("KeePass Search running. Press Alt+Shift+R to open search window.")
        print("Right-click the window for menu options.")
        self.root.mainloop()
