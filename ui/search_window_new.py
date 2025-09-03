import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Any, Dict
import time
import sys
import os

from .window_manager import WindowManager
from .hotkey_manager import HotkeyManager
from .window_relations_manager import WindowRelationsManager
from .state_manager import StateManager, AppState
from .view_manager import ViewManager
from .views import InitialView, SearchView, ResultsListView, EntryDetailsView
from .logger import Logger

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

# Get logger instance
logger = Logger.get_instance()

class SearchWindow:
    """Main window for KeePass Data Retriever application using modular view architecture"""
    
    def __init__(self, on_search: Callable, on_action: Callable, on_select: Callable, 
                 on_connect: Callable, on_get_recent_entries: Callable):
        """Initialize the search window with new view architecture"""
        # Create root window
        self.root = tk.Tk()
        
        # Initialize state manager
        self.state_manager = StateManager()
        
        # Initialize window components
        self.window = WindowManager(self.root)
        self.window_relations_manager = WindowRelationsManager()
        
        # Store callbacks
        self.on_search = on_search
        self.on_action = on_action
        self.on_select = on_select
        self.on_connect = on_connect
        self.on_get_recent_entries = on_get_recent_entries
        
        # Initialize view manager
        self.view_manager = ViewManager(self.window.get_main_frame(), self.state_manager)
        
        # Register views
        self._register_views()
        
        # Setup callbacks for views
        self._setup_view_callbacks()
        
        # Window state tracking
        self.active_window_title_at_last_hide: Optional[str] = None
        self.last_hotkey_time = 0
        
        # Bind global events
        self.root.bind('<Escape>', lambda e: self.hide())
        self.root.bind('<FocusOut>', self.window.check_focus)
        
        # Start hotkey listener
        self.hotkey = HotkeyManager(self.show_window)
        
        # Register as state listener
        self.state_manager.register_listener(self)
    
    def _register_views(self):
        """Register all view classes with the view manager"""
        self.view_manager.register_view('InitialView', InitialView)
        self.view_manager.register_view('SearchView', SearchView)
        self.view_manager.register_view('ResultsListView', ResultsListView)
        self.view_manager.register_view('EntryDetailsView', EntryDetailsView)
    
    def _setup_view_callbacks(self):
        """Setup callbacks for each view type"""
        # These will be called lazily when views are created
        pass
    
    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"SearchWindow: State changed to {state}")
        
        # Add common data to all state transitions
        if 'window_relations_manager' not in data:
            data['window_relations_manager'] = self.window_relations_manager
        
        # Handle window visibility
        if state == AppState.HIDDEN:
            self.hide()
        else:
            # Ensure window is visible and expanded for content states
            if state in [AppState.RESULTS_LIST, AppState.ENTRY_ACTIONS]:
                self.window.set_expanded(True)
            elif state == AppState.INITIAL:
                # Check if we have recent entries to determine expansion
                recent_entries = self.on_get_recent_entries() if self.on_get_recent_entries else []
                self.window.set_expanded(len(recent_entries) > 0)
            else:
                self.window.set_expanded(False)
    
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
            return
            
        current_time = time.time()
        self.window.show()
        
        # Determine if we need to reset to initial state
        current_app_state = self.state_manager.get_current_state()
        logger.debug(f"Current state before processing: {current_app_state}")
        
        context_changed = (self.active_window_title_at_last_hide is not None and 
                          self.active_window_title_at_last_hide != newly_logged_window_title)
        
        reset_to_initial = (
            context_changed or
            current_app_state == AppState.STARTING or
            current_time - self.last_hotkey_time > config.get_search_reset_timeout()
        )
        
        if reset_to_initial:
            logger.debug("Transitioning to INITIAL state")
            data = {'window_relations_manager': self.window_relations_manager}
            self.state_manager.transition_to(AppState.INITIAL, data)
        elif current_app_state == AppState.HIDDEN:
            # Restore to previous state or initial
            previous_state = self.state_manager.get_previous_state()
            if previous_state == AppState.INITIAL:
                data = {'window_relations_manager': self.window_relations_manager}
                self.state_manager.transition_to(AppState.INITIAL, data)
            else:
                # Try to restore previous state
                previous_data = self.state_manager.get_previous_state_data()
                if previous_state and previous_state != AppState.HIDDEN:
                    self.state_manager.transition_to(previous_state, previous_data)
                else:
                    data = {'window_relations_manager': self.window_relations_manager}
                    self.state_manager.transition_to(AppState.INITIAL, data)
        
        # Update last hotkey time
        self.last_hotkey_time = current_time
        
        # Setup view callbacks now that we have them available
        self._setup_active_view_callbacks()
        
        # Focus the active view
        active_view = self.view_manager.get_active_view()
        if active_view:
            self.root.after(100, active_view.focus)
    
    def _setup_active_view_callbacks(self):
        """Setup callbacks for the currently active view"""
        active_view = self.view_manager.get_active_view()
        if not active_view:
            return
        
        if isinstance(active_view, InitialView):
            active_view.set_callbacks(
                self.on_search,
                self.on_get_recent_entries,
                self.on_select,
                self.window_relations_manager
            )
        elif isinstance(active_view, SearchView):
            active_view.set_callbacks(
                self.on_search,
                self.on_select
            )
        elif isinstance(active_view, ResultsListView):
            active_view.set_callbacks(
                self.on_select,
                self.window_relations_manager
            )
        elif isinstance(active_view, EntryDetailsView):
            active_view.set_callbacks(
                self.on_action,
                self.window_relations_manager,
                self.hide
            )
    
    def hide(self):
        """Hide the window"""
        # Store the current window title when hiding
        self.active_window_title_at_last_hide = self.window_relations_manager.current_window_title
        logger.debug(f"Storing active_window_title_at_last_hide: '{self.active_window_title_at_last_hide}'")
        
        # Transition to HIDDEN state
        current_state = self.state_manager.get_current_state()
        if current_state != AppState.HIDDEN:
            self.state_manager.transition_to(AppState.HIDDEN)
        
        # Hide the window
        self.window.hide()
    
    def show_entries(self, entries: List[Any], keep_search_mode=True, skip_state_transition=False, is_recent_list: bool = False):
        """Show search results - adapter method for compatibility"""
        logger.debug(f"Showing {len(entries)} entries, keep_search_mode={keep_search_mode}, is_recent_list={is_recent_list}")
        
        if not entries:
            # Show search view with no results
            if not skip_state_transition:
                self.state_manager.transition_to(AppState.SEARCH, {
                    'search_term': '',
                    'entries': []
                })
            return
        
        if len(entries) == 1 and not keep_search_mode:
            # Single entry - show entry details directly
            entry = entries[0]
            if not skip_state_transition:
                self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})
        else:
            # Multiple entries or keep_search_mode is True
            if keep_search_mode:
                # Show in search view
                if not skip_state_transition:
                    self.state_manager.transition_to(AppState.SEARCH, {
                        'search_term': '',
                        'entries': entries
                    })
                # Update search view with results
                search_view = self.view_manager.get_view('SearchView')
                if search_view and search_view.is_active:
                    search_view.show_search_results(entries)
            else:
                # Show in results list view
                if not skip_state_transition:
                    self.state_manager.transition_to(AppState.RESULTS_LIST, {
                        'entries': entries,
                        'is_recent_list': is_recent_list
                    })
    
    def show_selected_entry(self, entry: Any, skip_state_transition=False):
        """Show selected entry - adapter method for compatibility"""
        logger.debug(f"Showing selected entry: {entry.title}")
        if not skip_state_transition:
            self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})
    
    def set_search_text(self, text: str):
        """Set the search input text - adapter method for compatibility"""
        # This will be handled by the active view
        active_view = self.view_manager.get_active_view()
        if hasattr(active_view, 'search_input'):
            active_view.search_input.delete(0, tk.END)
            active_view.search_input.insert(0, text)
    
    def set_status(self, text: str):
        """Set status text - adapter method for compatibility"""
        active_view = self.view_manager.get_active_view()
        if hasattr(active_view, 'status_display'):
            active_view.status_display.set_text(text)
    
    def run(self):
        """Start the application"""
        hotkey = config.get_search_hotkey()
        logger.info(f"KeePass Search running. Press {hotkey} to open search window.")
        logger.info("Right-click the window for menu options.")
        logger.info("Type /exit in any search box to exit the application.")
        self.root.mainloop()
    
    def cleanup(self):
        """Clean up resources"""
        if self.view_manager:
            self.view_manager.cleanup()
        if self.state_manager:
            self.state_manager.unregister_listener(self)