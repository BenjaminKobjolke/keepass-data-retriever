import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Any, Dict
import time
import sys
import os

from .window_manager import WindowManager
from .input_manager import InputManager, InputMode
from .status_display import StatusDisplay
from .results_view import ResultsView
from .hotkey_manager import HotkeyManager
from .dark_entry import DarkEntry
from .window_relations_manager import WindowRelationsManager
from .state_manager import StateManager, AppState
from .keyboard_handler import KeyboardHandler
from .entry_actions_handler import EntryActionsHandler
from .state_handler import StateHandler
from .logger import Logger

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

# Get logger instance
logger = Logger.get_instance()

class SearchWindow:
    """Main window for KeePass Data Retriever application"""
    
    def __init__(self, on_search: Callable, on_action: Callable, on_select: Callable, 
                 on_connect: Callable, on_get_recent_entries: Callable):
        """Initialize the search window"""
        # Initialize state manager
        self.state_manager = StateManager()
        
        # Create root window
        self.root = tk.Tk()
        
        self.active_window_title_at_last_hide: Optional[str] = None
        self.is_recent_list_active: bool = False # Flag to track if current list is from window-relations
        # Track last hotkey activation time
        self.last_hotkey_time = 0  # Initialize to 0 (epoch time)
        
        # Initialize window relations manager
        self.window_relations_manager = WindowRelationsManager()
        
        # Initialize components
        self.window = WindowManager(self.root)
        self.status = StatusDisplay(self.window.get_main_frame())
        
        # Store callbacks
        self.on_search = on_search
        self.on_action = on_action
        self.on_select = on_select
        self.on_connect = on_connect  # Callback for lazy database connection
        self.on_get_recent_entries = on_get_recent_entries  # Callback for getting recent entries
        
        # Initialize keyboard handler
        self.keyboard_handler = KeyboardHandler()
        
        # Initialize entry actions handler
        self.entry_actions_handler = EntryActionsHandler(
            self.root,
            self.window.get_main_frame(),
            self.state_manager,
            self.on_action,
            self.window_relations_manager,
            self.hide
        )
        
        # Initialize input manager
        self.input = InputManager(
            self.window.get_main_frame(),
            self._handle_search,
            self._handle_select,
            self.entry_actions_handler.handle_action,
            self.hide,
            self._handle_reset,
            DarkEntry,
            self.entry_actions_handler.handle_return_key,
            self._handle_highlight_change,
            self.entry_actions_handler.handle_highlight_change,
            self._handle_delete_recent_entry, # Callback for delete key
            self.show_initial_view,
            self.state_manager,  # Pass the state manager to InputManager
            self._handle_exit    # Pass the exit handler
        )
        
        # Initialize results view
        self.results = ResultsView(self.window.get_main_frame(), self.state_manager)
        
        # Initialize state handler
        self.state_handler = StateHandler(
            self.state_manager,
            self.on_search,
            self.on_get_recent_entries,
            self.show_entries,
            self.show_selected_entry,
            self._handle_reset,
            self.input.set_search_text,
            self.input.show_search
        )
        
        # Bind events
        self.root.bind('<Return>', self._handle_return)
        self.root.bind('<Escape>', lambda e: self.hide())
        self.root.bind('<FocusOut>', self.window.check_focus)
        
        # Start hotkey listener
        self.hotkey = HotkeyManager(self.show_window)
        
        # Register as state listener
        self.state_manager.register_listener(self)

    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"SearchWindow: State changed to {state}")
        
        # Add window_relations_manager to data for state handler
        if 'window_relations_manager' not in data:
            data['window_relations_manager'] = self.window_relations_manager
            
        # Let the state handler handle the state change
        if state != AppState.HIDDEN:
            self.state_handler.handle_state_change(state, data)
        elif state == AppState.HIDDEN:
            # Hide window directly
            self.hide()

    def _handle_search(self, search_term: str):
        """Handle search request"""
        logger.debug(f"Search request with term: '{search_term}'")
        # Transition to SEARCH state
        self.state_manager.transition_to(AppState.SEARCH, {'search_term': search_term})
        # Perform the actual search
        self.on_search(search_term)

    def _handle_select(self, entry: Any):
        """Handle entry selection"""
        logger.debug(f"Entry selected: {entry.title}")
        # Transition to ENTRY_ACTIONS state
        self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})
        # Don't create action buttons here, let show_selected_entry handle it
        self.on_select(entry)

    def _handle_reset(self):
        """Handle reset request"""
        logger.debug("Reset request")
        
        # Clear results and actions
        self.results.clear()
        self.entry_actions_handler.cleanup()

        # If _handle_reset is called and it's not for showing a recent list,
        # then the "recent list active" flag should be false.
        # This will be set to true if show_recent_entries or show_entries(is_recent_list=True) is called.
        # A bit indirect, but show_entries will manage self.is_recent_list_active.
        # For now, let's assume if we are resetting and not immediately showing recent entries,
        # it's not a recent list.
        # A better place to set this is in show_entries itself.

        # Check if we're in INITIAL state and handling a new window
        current_state = self.state_manager.get_current_state()
        # If this reset is part of transitioning to INITIAL or a direct search,
        # then the list shown (if any) won't be "recent entries" in the deletable sense.
        # The `is_recent_list_active` flag is managed by `show_entries`.
        # So, if `self.input.entries` exists and we are showing them, `show_entries` will be called,
        # and it will use its `is_recent_list` parameter (defaulting to False)
        # to set `self.is_recent_list_active`.
        
        # The logic below for showing `self.input.entries` will call `show_entries`
        # which will set `is_recent_list_active` to False by default.
        # If this reset is part of initial view, `show_recent_entries` will later call `show_entries` with `is_recent_list=True`.

        # Check if we're in INITIAL state and handling a new window
        current_state = self.state_manager.get_current_state()
        if current_state == AppState.INITIAL:
            # We're in INITIAL state, so we should clear any entries from previous windows
            # This prevents entries from a previous window being shown for the current window
            logger.debug("In INITIAL state, clearing entries from previous windows")
            self.input.entries = []
            self.window.set_expanded(False)
            self.status.set_text("")
            return

        # Check if we have entries to show
        if self.input.entries and len(self.input.entries) > 0:
            logger.debug(f"Showing {len(self.input.entries)} entries")
            # Show the entries (skip state transition to avoid infinite loop)
            self.show_entries(self.input.entries, keep_search_mode=True, skip_state_transition=True, is_recent_list=False) # These are restored, not "recent" in deletable sense
            self.window.set_expanded(True)
            self.status.set_text("Recent entries for this window:")
            
            # Make sure the entries are visible
            self.results.frame.pack(fill=tk.BOTH, expand=True)
        else:
            logger.debug("No entries to show")
            self.window.set_expanded(False)
            self.status.set_text("")

    def _handle_return(self, event):
        """Handle Return key"""
        # If we're in action mode, let the entry actions handler handle it
        if self.input.current_mode == InputMode.ACTION and self.input.current_entry:
            if self.entry_actions_handler.handle_action_return(self.input.current_entry):
                return "break"
        return self.input.handle_return()

    def show_window(self):
        """Show the window"""
        newly_logged_window_title = None
        try:
            newly_logged_window_title = self.window_relations_manager.log_active_window()
            logger.debug(f"Active window title after logging: {newly_logged_window_title}")
        except Exception as e:
            logger.error(f"Error logging active window: {e}")
            
        # First check if we need to connect to the database
        if not self.on_connect():
            # Connection failed or was cancelled, don't show window
            return
            
        current_time = time.time()
        # Show the window only after successful database connection
        self.window.show()
        
        # Get current state
        current_app_state = self.state_manager.get_current_state()
        logger.debug(f"Current state before processing: {current_app_state}, last hidden title: '{self.active_window_title_at_last_hide}', new title: '{newly_logged_window_title}'")

        # Determine if window context changed since last hide
        context_changed = False
        if self.active_window_title_at_last_hide is not None and \
           self.active_window_title_at_last_hide != newly_logged_window_title:
            logger.info(f"Window context changed from '{self.active_window_title_at_last_hide}' to '{newly_logged_window_title}'. Triggering reset to INITIAL.")
            context_changed = True

        # Conditions for resetting to INITIAL state
        reset_to_initial = False
        reset_reason = ""

        if context_changed:
            reset_to_initial = True
            reset_reason = "context changed"
        elif current_app_state == AppState.STARTING:
            reset_to_initial = True
            reset_reason = "first time showing window"
        elif current_time - self.last_hotkey_time > config.get_search_reset_timeout():
            reset_to_initial = True
            reset_reason = "search reset timeout exceeded"

        if reset_to_initial:
            logger.debug(f"{reset_reason}, transitioning to INITIAL state")
            data = {'window_relations_manager': self.window_relations_manager}
            self.state_manager.transition_to(AppState.INITIAL, data)
        elif current_app_state == AppState.HIDDEN:
            previous_state = self.state_manager.get_previous_state()
            logger.debug(f"Coming from HIDDEN state (no reset conditions met), previous state was: {previous_state}")
            
            if previous_state == AppState.INITIAL:
                logger.debug("Previous state was INITIAL, transitioning back to INITIAL with window_relations_manager")
                data = {'window_relations_manager': self.window_relations_manager}
                self.state_manager.transition_to(AppState.INITIAL, data)
            else:
                logger.debug("Attempting to restore previous state (from HIDDEN)")
                if not self.state_handler.restore_previous_state():
                    logger.debug("No previous state to restore, using default restore_last_mode")
                    self.input.restore_last_mode()
        else:
            logger.debug(f"Not STARTING, not HIDDEN, no reset conditions met. Current state: {current_app_state}. Attempting to restore previous state or current mode.")
            if not self.state_handler.restore_previous_state():
                logger.debug("No previous state to restore, using default restore_last_mode")
                self.input.restore_last_mode()
        
        # Update last hotkey time
        self.last_hotkey_time = current_time
        
        # Schedule an additional focus call after a short delay
        self.root.after(100, self._ensure_focus)
        
    def show_recent_entries(self, entries):
        """Show recent entries for the current window"""
        self.state_handler.show_recent_entries(entries)
        
    def show_initial_view(self):
        """Show the initial view with recent entries for the current window"""
        # Transition to INITIAL state
        self.state_manager.transition_to(AppState.INITIAL)
    
    def _ensure_focus(self):
        """Ensure the current input has focus"""
        logger.debug(f"Ensuring focus for mode: {self.input.current_mode}")
            
        if self.input.current_mode == InputMode.SEARCH:
            logger.debug("Focusing search input")
            self.input.search_input.focus_force()
        elif self.input.current_mode == InputMode.LIST:
            logger.debug("Focusing list input")
            self.input.list_input.focus_force()
        elif self.input.current_mode == InputMode.ACTION:
            logger.debug("Focusing action input")
            self.input.action_input.focus_force()

    def hide(self):
        """Hide the window"""
        # Store the current window title when hiding. This title is associated with the UI state before hiding.
        self.active_window_title_at_last_hide = self.window_relations_manager.current_window_title
        logger.debug(f"Storing active_window_title_at_last_hide: '{self.active_window_title_at_last_hide}'")

        # Get current state and data before transitioning to HIDDEN
        current_state = self.state_manager.get_current_state()
        current_data = self.state_manager.get_state_data()
        
        # Only transition to HIDDEN if we're not already in HIDDEN state
        if current_state != AppState.HIDDEN:
            # Store the current entries in the input manager for restoration
            if self.input.entries:
                logger.debug(f"Storing {len(self.input.entries)} entries before hiding")
                
            # Transition to HIDDEN state
            self.state_manager.transition_to(AppState.HIDDEN)
            
        # Hide the window
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
            
    def _handle_delete_recent_entry(self, entry_to_delete: Any):
        """Handle delete request for a recent entry"""
        if not self.is_recent_list_active:
            logger.debug("Delete key pressed, but not in recent list mode. Ignoring.")
            return

        if not entry_to_delete:
            logger.warning("Delete recent entry requested, but no entry is selected.")
            return

        current_window_title = self.window_relations_manager.current_window_title
        if not current_window_title:
            logger.warning("Delete recent entry requested, but current window title is unknown.")
            return

        try:
            entry_uuid = str(entry_to_delete.uuid)
            logger.info(f"Requesting deletion of recent entry UUID '{entry_uuid}' for window '{current_window_title}'.")
            self.window_relations_manager.remove_recent_entry(current_window_title, entry_uuid)
            # Refresh the view by transitioning to INITIAL state, which re-fetches recent entries
            logger.debug("Transitioning to INITIAL state to refresh recent entries view after deletion.")
            self.state_manager.transition_to(AppState.INITIAL, {'window_relations_manager': self.window_relations_manager})
        except AttributeError:
            logger.error(f"Failed to get UUID from entry: {entry_to_delete}. Cannot delete.")
        except Exception as e:
            logger.error(f"Error during recent entry deletion: {e}")

    def show_entries(self, entries: List[Any], keep_search_mode=True, skip_state_transition=False, is_recent_list: bool = False):
        """Show search results"""
        logger.debug(f"Showing {len(entries)} entries, keep_search_mode={keep_search_mode}, is_recent_list={is_recent_list}")
        
        self.is_recent_list_active = is_recent_list # Update flag based on current call

        # Clear previous results
        self.results.clear()
        self.entry_actions_handler.cleanup()
        
        if not entries:
            self.window.set_expanded(False)
            self.status.set_text("No entries found")
            return
            
        if len(entries) == 1 and not keep_search_mode:
            # Single entry - show actions directly
            entry = entries[0]
            
            # Transition to ENTRY_ACTIONS state (unless skipped)
            if not skip_state_transition:
                self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})
            
            self.window.set_expanded(True)
            self.status.show_search_results(entries, entry)
            
            # Set the entry in InputManager before showing actions
            logger.debug("Single entry, showing actions")
            self.input.show_list(entries)  # This will set current_entry and call show_actions
            
            # Show the selected entry with action buttons
            self.entry_actions_handler.show_selected_entry(entry)
        
        else:
            # Multiple entries or keep_search_mode is True
            
            # Transition to RESULTS_LIST state (unless skipped)
            if not skip_state_transition:
                self.state_manager.transition_to(AppState.RESULTS_LIST, {'entries': entries})
            
            self.window.set_expanded(True)
            self.results.show_entries(entries, is_recent_list=is_recent_list)
            self.status.show_search_results(entries)
            
            if keep_search_mode:
                # Store entries but keep search input active
                logger.debug("Keeping search input active")
                self.input.entries = entries.copy()
                # Don't highlight any entry by default
                self.input.current_entry = None
                self.results.current_highlight = -1
                # Ensure we're in search mode
                self.input.show_search()
            else:
                # Show list mode
                logger.debug("Showing list mode")
                self.input.show_list(entries)
                
                # Highlight the first entry by default
                if entries:
                    entry = self.results.highlight_entry(0)
                    if entry:
                        self.input.current_entry = entry

    def show_selected_entry(self, entry: Any, skip_state_transition=False):
        """Show selected entry"""
        logger.debug(f"Showing selected entry: {entry.title}")
        self.results.clear()
        self.status.show_selected_entry(entry)
        
        # Ensure InputManager has the current entry before showing actions
        self.input.current_entry = entry
        self.input.show_actions()
        
        # Show the selected entry with action buttons
        self.entry_actions_handler.show_selected_entry(entry)

    def set_search_text(self, text: str):
        """Set the search input text"""
        self.input.set_search_text(text)

    def set_status(self, text: str):
        """Set status text"""
        self.status.set_text(text)

    def _handle_exit(self):
        """Handle exit command"""
        logger.info("Exit command detected, closing application")
        if self.root:
            self.root.quit()
            
    def run(self):
        """Start the application"""
        hotkey = config.get_search_hotkey()
        logger.info(f"KeePass Search running. Press {hotkey} to open search window.")
        logger.info("Right-click the window for menu options.")
        logger.info("Type /exit in any search box to exit the application.")
        self.root.mainloop()
