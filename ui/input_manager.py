import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Type, Dict, Any
from enum import Enum, auto
from .state_manager import StateManager, AppState
from .logger import Logger

# Get logger instance
logger = Logger.get_instance()

class InputMode(Enum):
    SEARCH = auto()
    LIST = auto()
    ACTION = auto()

class InputManager:
    def __init__(self, parent: ttk.Frame, on_search: Callable, on_select: Callable, 
                 on_action: Callable, on_escape: Callable, on_reset: Callable, 
                 entry_class: Type[ttk.Entry], on_enter_action: Callable = None,
                 on_highlight_change: Callable = None, on_action_highlight_change: Callable = None,
                 on_show_initial_view: Callable = None, state_manager: StateManager = None,
                 on_exit: Callable = None):
        self.on_search = on_search
        self.on_select = on_select
        self.on_action = on_action
        self.on_escape = on_escape
        self.on_reset = on_reset
        self.on_enter_action = on_enter_action
        self.on_highlight_change = on_highlight_change
        self.on_action_highlight_change = on_action_highlight_change
        self.on_show_initial_view = on_show_initial_view
        self.state_manager = state_manager
        self.on_exit = on_exit  # Callback for exiting the application
        
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
        self.search_input.bind('<Up>', self._handle_search_arrow_up)
        self.search_input.bind('<Down>', self._handle_search_arrow_down)
        # Removed KeyRelease bindings to prevent double navigation
        self.search_input.bind('<BackSpace>', self._handle_search_backspace)
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
        
        # Register as state listener if state manager is provided
        if self.state_manager:
            self.state_manager.register_listener(self)
    
    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"InputManager: State changed to {state}")
        
        if state == AppState.INITIAL or state == AppState.SEARCH:
            self.show_search()
            if state == AppState.SEARCH:
                search_term = data.get('search_term', '')
                if search_term:
                    self.set_search_text(search_term)
        elif state == AppState.RESULTS_LIST:
            # Don't store entries here - let SearchWindow handle it
            # This prevents duplicate entries
            pass
        elif state == AppState.ENTRY_ACTIONS:
            entry = data.get('entry')
            if entry:
                self.current_entry = entry
                self.show_actions()

    def _handle_escape(self, event):
        """Handle ESC key"""
        self.on_escape()
        return "break"

    def _handle_search(self, event):
        """Handle search entry Return key"""
        logger.debug(f"_handle_search called, entries: {len(self.entries) if self.entries else 0}, current_entry: {self.current_entry is not None}")
        
        # Check for exit command
        search_term = self.search_input.get()
        if search_term == "/exit" and self.on_exit:
            logger.info("Exit command detected")
            self.on_exit()
            return "break"
            
        # If we have entries and a current entry is selected, select it
        if self.entries and self.current_entry:
            logger.debug("Selecting current entry")
            self.on_select(self.current_entry)
        elif search_term.strip():  # Only perform search if search term is not empty
            # Otherwise perform a search
            logger.debug(f"Performing search with term: '{search_term}'")
            self.on_search(search_term)
        else:
            logger.debug("Empty search term, ignoring Enter key")
        return "break"
        
    def _handle_search_backspace(self, event):
        """Handle backspace key in search input"""
        # Only handle backspace if the search input is empty and we have entries
        if not self.search_input.get() and self.entries:
            logger.debug("Backspace pressed in search mode with empty input, resetting to initial view")
            self.reset_to_initial_view()  # Reset to initial view
            return "break"
        # Otherwise, let the default backspace behavior happen
        return False
        
    def _handle_search_arrow_up(self, event):
        """Handle up arrow key in search input"""
        if self.entries:
            # If we're already at the first entry or no entry is selected,
            # we don't want to do anything (let SearchWindow handle it)
            if self.current_entry is None or self.on_highlight_change is None:
                return "break"
            
            # Otherwise, navigate to the previous entry
            self._navigate_previous()
            return "break"
        return False
        
    def _handle_search_arrow_down(self, event):
        """Handle down arrow key in search input"""
        if self.entries:
            self._navigate_next()
            return "break"
        return False

    def _handle_list_key(self, event):
        """Handle key press in list selection input"""
        logger.debug(f"List key pressed: {event.char}, keysym: {event.keysym}")
        
        # Check for exit command
        if self.list_input.get() == "/exit" and self.on_exit:
            logger.info("Exit command detected")
            self.on_exit()
            return "break"
            
        # Handle Backspace key to go back to main GUI
        if event.keysym == 'BackSpace':
            self.reset_to_search()  # Reset state and go back to search
            return "break"
        
        # Handle arrow keys for navigation
        if event.keysym == 'Up':
            self._navigate_previous()
            return "break"
        elif event.keysym == 'Down':
            self._navigate_next()
            return "break"
        elif event.keysym == 'Return':
            # Select the currently highlighted entry if any
            if self.current_entry:
                self.on_select(self.current_entry)
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
        
    def _navigate_previous(self):
        """Navigate to the previous entry in the list"""
        if self.on_highlight_change and self.entries:
            self.on_highlight_change('up')
            
    def _navigate_next(self):
        """Navigate to the next entry in the list"""
        if self.on_highlight_change and self.entries:
            self.on_highlight_change('down')

    def _handle_action_key(self, event):
        """Handle key press in action selection input"""
        logger.debug(f"Action key pressed: {event.char}, keysym: {event.keysym}")
        
        # Check for exit command
        if self.action_input.get() == "/exit" and self.on_exit:
            logger.info("Exit command detected")
            self.on_exit()
            return "break"
            
        # Handle Backspace key to go back to main GUI
        if event.keysym == 'BackSpace':
            logger.debug("Backspace pressed in action mode, returning to search")
            # Store entries before resetting
            stored_entries = self.entries.copy() if self.entries else []
            logger.debug(f"Stored {len(stored_entries)} entries")
            
            self.reset_to_search()  # Reset state and go back to search
            
            # Restore entries after reset
            logger.debug(f"Restored {len(self.entries)} entries")
            return "break"
            
        # Handle arrow keys for navigation
        if event.keysym == 'Up':
            self._navigate_action_previous()
            return "break"
        elif event.keysym == 'Down':
            self._navigate_action_next()
            return "break"
        # Let the Return key event propagate to SearchWindow._handle_return
            
        if event.char == '0':
            self.reset_to_search()  # Reset state and go back to search
        elif event.char.isdigit():
            number = int(event.char)
            if 1 <= number <= 7:  # Now handling 7 actions
                actions = [
                    'auto_type',     # 1: Auto Type
                    'username',      # 2: Copy Username
                    'password',      # 3: Copy Password
                    'type_username', # 4: Type Username
                    'type_password', # 5: Type Password
                    'url',           # 6: Copy URL
                    'open_url',      # 7: Open URL
                ]
                # Check if the action exists (URL actions might not be available)
                if number <= len(actions):
                    self.on_action(actions[number - 1], self.current_entry)
                    # Hide window after any action
                    self.on_escape()
        
        # Clear the input
        self.action_input.delete(0, tk.END)
        return "break"
        
    def _navigate_action_previous(self):
        """Navigate to the previous action"""
        if self.on_action_highlight_change and self.current_entry:
            self.on_action_highlight_change('up')
            
    def _navigate_action_next(self):
        """Navigate to the next action"""
        if self.on_action_highlight_change and self.current_entry:
            self.on_action_highlight_change('down')

    def reset_to_initial_view(self):
        """Reset to initial view and clear entries"""
        logger.debug(f"Resetting to initial view, clearing {len(self.entries) if self.entries else 0} entries")
        
        # Clear the entries
        self.entries = []
        
        # Don't highlight any entry by default
        self.current_entry = None
        
        # Ensure we're in search mode
        self.show_search()
        
        # If we have a state manager, transition to INITIAL state
        if self.state_manager:
            # Add a flag to indicate we're clearing entries
            self.state_manager.transition_to(AppState.INITIAL, {'clear_entries': True})
        
        # If we have a callback to show the initial view, call it
        if self.on_show_initial_view:
            self.on_show_initial_view()
        else:
            # Otherwise, just clear the search input and call on_reset
            self.set_search_text("")
            self.on_reset()
            
    def reset_to_search(self):
        """Reset state and return to search input"""
        # Store entries temporarily
        stored_entries = self.entries.copy() if self.entries else []
        
        # Reset state
        self.entries = []
        self.current_entry = None
        self.on_reset()  # Call reset callback to clear results
        
        # Show search input
        self.show_search()
        
        # Restore entries
        self.entries = stored_entries
        
        # If we have a state manager, transition to SEARCH state
        if self.state_manager:
            self.state_manager.transition_to(AppState.SEARCH, {'entries': self.entries})
        
        # If we have entries, tell the SearchWindow to show them
        if self.entries and len(self.entries) > 0:
            logger.debug(f"Restoring {len(self.entries)} entries after reset")
            # We need to call on_reset again to show the entries
            self.on_reset()

    def show_search(self):
        """Show search input"""
        logger.debug(f"show_search called from {__import__('traceback').extract_stack()[-2][2]}")
        self.list_input.grid_remove()
        self.action_input.grid_remove()
        self.search_input.grid()
        self.search_input.focus_force()
        self.search_input.select_range(0, tk.END)
        self.current_mode = InputMode.SEARCH
        logger.debug(f"Input mode set to {self.current_mode}")

    def show_list(self, entries):
        """Show list selection input"""
        logger.debug(f"show_list called from {__import__('traceback').extract_stack()[-2][2]} with {len(entries)} entries")
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
        logger.debug("Moving focus to list input")
        logger.debug(f"Input mode set to {self.current_mode}")

    def show_actions(self):
        """Show action selection input"""
        self.search_input.grid_remove()
        self.list_input.grid_remove()
        
        # Make the action input minimal but still visible
        self.action_input.grid()
        
        # Make it blend in with the background - use a fixed dark color
        # that matches the application's dark theme
        self.action_input.configure(
            background='#1e1e1e',  # Dark background color
            highlightthickness=0,  # No border
            width=1  # Very small width
        )
        
        # Position it at the bottom with minimal space
        self.action_input.grid(pady=(0, 1))
        
        self.action_input.focus_force()  # Give it focus for keyboard input
        
        self.current_mode = InputMode.ACTION
        logger.debug("Moving focus to action input (minimal)")

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
        logger.debug("Action Return key pressed")
        # Let the SearchWindow._handle_return method handle this
        # by not returning "break" here
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
