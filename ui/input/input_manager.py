"""Input management for KeePass Data Retriever."""

import tkinter as tk
from tkinter import ttk
from typing import Type, Dict, Any
from enum import Enum, auto
from ..state_manager import StateManager, AppState
from ..logger import Logger
from ..theme_manager import ThemeManager
from ..mode_indicator import ModeIndicator
from ..action_registry import ActionRegistry
from ..events import EventBus, Events
from .command_handler import CommandHandler
from config import config

# Get logger instance
logger = Logger.get_instance()


class InputMode(Enum):
    SEARCH = auto()
    LIST = auto()
    ACTION = auto()


class InputManager:
    """Manages input fields and keyboard handling for different modes."""

    def __init__(self, parent: ttk.Frame, entry_class: Type[ttk.Entry],
                 state_manager: StateManager = None):
        self.state_manager = state_manager

        # Create command handler for /exit, /reload, /settings
        self.command_handler = CommandHandler()

        # Create mode indicator above input
        self.mode_indicator = ModeIndicator(parent, "SEARCH")

        # Create input frame to position all inputs
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.frame.pack(padx=2, pady=2)

        input_width = max(30, int(config.get_window_width() / 10.5))

        # Create search entry
        self.search_input = entry_class(self.frame, width=input_width)
        self.search_input.grid(row=0, column=0)

        # Create list selection input
        self.list_input = entry_class(self.frame, width=input_width)
        self.list_input.grid(row=0, column=0)
        self.list_input.grid_remove()  # Hide initially

        # Create action selection input
        self.action_input = entry_class(self.frame, width=input_width)
        self.action_input.grid(row=0, column=0)
        self.action_input.grid_remove()  # Hide initially

        # Bind events
        self.search_input.bind('<Return>', self._handle_search)
        self.search_input.bind('<Up>', self._handle_search_arrow_up)
        self.search_input.bind('<Down>', self._handle_search_arrow_down)
        self.search_input.bind('<BackSpace>', self._handle_search_backspace)
        self.search_input.bind('<KeyRelease>', self._handle_filter_input)
        self.list_input.bind('<Key>', self._handle_list_key)
        self.action_input.bind('<Key>', self._handle_action_key)
        self.action_input.bind('<Return>', self._handle_action_return)

        # Bind Delete key to search and list inputs
        self.search_input.bind('<Delete>', self._handle_delete_key)
        self.list_input.bind('<Delete>', self._handle_delete_key)

        # Bind ESC key to all inputs
        self.search_input.bind('<Escape>', self._handle_escape)
        self.list_input.bind('<Escape>', self._handle_escape)
        self.action_input.bind('<Escape>', self._handle_escape)

        self.entries = []  # Store entries for list selection (may be filtered)
        self.original_entries = []  # Store original unfiltered entries
        self.current_entry = None  # Store single entry for action mode
        self.current_mode = InputMode.SEARCH

        # Register as state listener if state manager is provided
        if self.state_manager:
            self.state_manager.register_listener(self)

    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"InputManager: State changed to {state}")

        # Update mode indicator based on state
        if state == AppState.INITIAL:
            # Only show RECENT if there are entries to display
            entries = data.get('entries', [])
            if entries:
                self.mode_indicator.set_mode("RECENT")
            else:
                self.mode_indicator.set_mode("SEARCH")
        elif state == AppState.SEARCH:
            self.mode_indicator.set_mode("SEARCH")
        elif state == AppState.RESULTS_LIST:
            self.mode_indicator.set_mode("RESULTS")
        elif state == AppState.ENTRY_ACTIONS:
            self.mode_indicator.set_mode("ACTIONS")

        if state == AppState.INITIAL or state == AppState.SEARCH:
            self.show_search()
            if state == AppState.SEARCH:
                search_term = data.get('search_term', '')
                if search_term:
                    self.set_search_text(search_term)
        elif state == AppState.RESULTS_LIST:
            # Don't store entries here - let SearchWindow handle it
            pass
        elif state == AppState.ENTRY_ACTIONS:
            entry = data.get('entry')
            if entry:
                self.current_entry = entry
                self.show_actions()

    def _handle_escape(self, event):
        """Handle ESC key"""
        EventBus.publish(Events.HIDE)
        return "break"

    def _clear_search_input(self):
        """Clear the search input field"""
        self.search_input.delete(0, tk.END)

    def _handle_search(self, event):
        """Handle search entry Return key"""
        logger.debug(f"_handle_search called, entries: {len(self.entries) if self.entries else 0}, current_entry: {self.current_entry is not None}")

        search_term = self.search_input.get()

        # Check for commands using CommandHandler
        if self.command_handler.try_execute(search_term, self._clear_search_input):
            return "break"

        # If we have entries and a current entry is selected, select it
        if self.entries and self.current_entry:
            logger.debug("Selecting current entry")
            EventBus.publish(Events.SELECT, self.current_entry)
        elif search_term.strip():  # Only perform search if search term is not empty
            logger.debug(f"Performing search with term: '{search_term}'")
            EventBus.publish(Events.SEARCH, search_term)
        else:
            logger.debug("Empty search term, ignoring Enter key")
        return "break"

    def _handle_search_backspace(self, event):
        """Handle backspace key in search input"""
        if not self.search_input.get() and self.entries:
            logger.debug("Backspace pressed in search mode with empty input, resetting to initial view")
            self.reset_to_initial_view()
            return "break"
        return False

    def _handle_filter_input(self, event):
        """Handle key release in search input for filtering results"""
        # Skip special keys that don't change text
        if event.keysym in ('Return', 'Up', 'Down', 'Escape', 'Delete', 'Tab',
                            'Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                            'Alt_L', 'Alt_R', 'Left', 'Right', 'Home', 'End'):
            return

        # Only filter if we have original entries to filter
        if not self.original_entries:
            return

        filter_text = self.search_input.get().strip().lower()

        if not filter_text:
            # Empty filter - restore all original entries
            self.entries = self.original_entries.copy()
            EventBus.publish(Events.FILTER, self.entries)
            return

        # Filter entries by title, username, and URL (case-insensitive)
        filtered = []
        for entry in self.original_entries:
            title = getattr(entry, 'title', '') or ''
            username = getattr(entry, 'username', '') or ''
            url = getattr(entry, 'url', '') or ''

            if (filter_text in title.lower() or
                filter_text in username.lower() or
                filter_text in url.lower()):
                filtered.append(entry)

        self.entries = filtered
        self.current_entry = None  # Reset highlight when filtering
        EventBus.publish(Events.FILTER, self.entries)

    def _handle_search_arrow_up(self, event):
        """Handle up arrow key in search input"""
        if self.entries:
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

        # Check for commands using CommandHandler
        if self.command_handler.try_execute(self.list_input.get()):
            return "break"

        # Handle Backspace key to go back to main GUI
        if event.keysym == 'BackSpace':
            self.reset_to_search()
            return "break"

        # Handle arrow keys for navigation
        if event.keysym == 'Up':
            self._navigate_previous()
            return "break"
        elif event.keysym == 'Down':
            self._navigate_next()
            return "break"
        elif event.keysym == 'Return':
            if self.current_entry:
                EventBus.publish(Events.SELECT, self.current_entry)
            return "break"

        if event.char == '0':
            self.reset_to_search()
        elif event.char.isdigit():
            number = int(event.char)
            if number <= len(self.entries):
                selected_entry = self.entries[number - 1]
                self.current_entry = selected_entry
                EventBus.publish(Events.SELECT, selected_entry)

        # Clear the input
        self.list_input.delete(0, tk.END)
        return "break"

    def _navigate_previous(self):
        """Navigate to the previous entry in the list"""
        if self.entries:
            EventBus.publish(Events.HIGHLIGHT_CHANGE, 'up')

    def _navigate_next(self):
        """Navigate to the next entry in the list"""
        if self.entries:
            EventBus.publish(Events.HIGHLIGHT_CHANGE, 'down')

    def _handle_action_key(self, event):
        """Handle key press in action selection input"""
        logger.debug(f"Action key pressed: {event.char}, keysym: {event.keysym}")

        # Check for commands using CommandHandler
        if self.command_handler.try_execute(self.action_input.get()):
            return "break"

        # Handle Backspace key to go back to main GUI
        if event.keysym == 'BackSpace':
            logger.debug("Backspace pressed in action mode, returning to search")
            stored_entries = self.entries.copy() if self.entries else []
            logger.debug(f"Stored {len(stored_entries)} entries")
            self.reset_to_search()
            logger.debug(f"Restored {len(self.entries)} entries")
            return "break"

        # Handle arrow keys for navigation
        if event.keysym == 'Up':
            self._navigate_action_previous()
            return "break"
        elif event.keysym == 'Down':
            self._navigate_action_next()
            return "break"

        if event.char == '0':
            self.reset_to_search()
        elif event.char.isdigit():
            action = ActionRegistry.get_action_by_key(event.char)
            if action:
                EventBus.publish(Events.ACTION, {'action_id': action['id'], 'entry': self.current_entry})
                EventBus.publish(Events.HIDE)

        # Clear the input
        self.action_input.delete(0, tk.END)
        return "break"

    def _navigate_action_previous(self):
        """Navigate to the previous action"""
        if self.current_entry:
            EventBus.publish(Events.ACTION_HIGHLIGHT_CHANGE, 'up')

    def _navigate_action_next(self):
        """Navigate to the next action"""
        if self.current_entry:
            EventBus.publish(Events.ACTION_HIGHLIGHT_CHANGE, 'down')

    def reset_to_initial_view(self):
        """Reset to initial view and clear entries"""
        logger.debug(f"Resetting to initial view, clearing {len(self.entries) if self.entries else 0} entries")

        self.entries = []
        self.original_entries = []
        self.current_entry = None
        self.show_search()

        if self.state_manager:
            self.state_manager.transition_to(AppState.INITIAL, {'clear_entries': True})

        EventBus.publish(Events.SHOW_INITIAL)

    def reset_to_search(self):
        """Reset state and return to search input"""
        stored_entries = self.entries.copy() if self.entries else []

        self.entries = []
        self.current_entry = None
        EventBus.publish(Events.RESET)

        self.show_search()

        self.entries = stored_entries

        if self.state_manager:
            self.state_manager.transition_to(AppState.SEARCH, {'entries': self.entries})

        if self.entries and len(self.entries) > 0:
            logger.debug(f"Restoring {len(self.entries)} entries after reset")
            EventBus.publish(Events.RESET)

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

    def set_entries(self, entries):
        """Set entries and store as original for filtering"""
        self.entries = entries.copy() if entries else []
        self.original_entries = entries.copy() if entries else []
        self.current_entry = None

    def show_list(self, entries):
        """Show list selection input"""
        logger.debug(f"show_list called from {__import__('traceback').extract_stack()[-2][2]} with {len(entries)} entries")
        self.set_entries(entries)

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

        self.action_input.grid()

        self.action_input.configure(
            background=ThemeManager.get_color('bg_color'),
            highlightthickness=0,
            width=1
        )

        self.action_input.grid(pady=(0, 1))
        self.action_input.focus_force()

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
            self.show_search()

    def set_search_text(self, text: str):
        """Set the search input text"""
        self.search_input.delete(0, tk.END)
        self.search_input.insert(0, text)

    def _handle_action_return(self, event):
        """Handle Return key in action input"""
        logger.debug("Action Return key pressed")
        return False

    def _handle_delete_key(self, event):
        """Handle Delete key in search or list mode"""
        logger.debug(f"Delete key pressed in mode: {self.current_mode}")
        if self.current_entry:
            EventBus.publish(Events.DELETE_ENTRY, self.current_entry)
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
