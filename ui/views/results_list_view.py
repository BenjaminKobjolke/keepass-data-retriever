import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Callable
from ..base_view import BaseView
from ..state_manager import AppState
from ..status_display import StatusDisplay
from ..results_view import ResultsView
from ..dark_entry import DarkEntry
from ..logger import Logger

logger = Logger.get_instance()

class ResultsListView(BaseView):
    """View for navigating multiple search results with keyboard"""
    
    def __init__(self, parent: tk.Widget, state_manager, view_manager):
        self.on_select: Callable = None
        self.window_relations_manager = None
        
        # UI components
        self.list_input = None
        self.status_display = None
        self.results_view = None
        
        # Results state
        self.current_entries = []
        self.is_recent_list = False
        
        super().__init__(parent, state_manager, view_manager)
    
    def set_callbacks(self, on_select: Callable, window_relations_manager):
        """Set callback functions for this view"""
        self.on_select = on_select
        self.window_relations_manager = window_relations_manager
    
    def get_supported_states(self) -> List[AppState]:
        """Return list of application states this view supports"""
        return [AppState.RESULTS_LIST]
    
    def create_ui(self):
        """Create the UI elements for results list view"""
        # Create list navigation input (hidden input for key handling)
        input_frame = ttk.Frame(self.container, style='Dark.TFrame')
        input_frame.pack(padx=2, pady=2)
        
        self.list_input = DarkEntry(input_frame, width=40)
        self.list_input.pack()
        
        # Bind events
        self.list_input.bind('<Key>', self._handle_key)
        self.list_input.bind('<Return>', self._handle_return)
        self.list_input.bind('<Up>', self._handle_arrow_up)
        self.list_input.bind('<Down>', self._handle_arrow_down)
        self.list_input.bind('<Delete>', self._handle_delete_key)
        self.list_input.bind('<Escape>', self._handle_escape)
        self.list_input.bind('<BackSpace>', self._handle_backspace)
        
        # Create status display
        self.status_display = StatusDisplay(self.container)
        
        # Create results view
        self.results_view = ResultsView(self.container, self.state_manager)
    
    def on_show(self, data: Dict[str, Any]):
        """Called when the view is shown"""
        logger.debug("ResultsListView: on_show")
        
        # Get entries and recent list flag from data
        self.current_entries = data.get('entries', [])
        self.is_recent_list = data.get('is_recent_list', False)
        
        if self.current_entries:
            # Show results
            self.results_view.show_entries(self.current_entries, is_recent_list=self.is_recent_list)
            
            # Set status text
            if self.is_recent_list:
                self.status_display.set_text("Recent entries for this window:")
            else:
                self.status_display.show_search_results(self.current_entries)
            
            # Highlight first entry by default
            entry = self.results_view.highlight_entry(0)
            
            # Clear the input field and make it invisible (it's just for key handling)
            self.list_input.delete(0, tk.END)
            
            # Ensure list input has focus for keyboard navigation
            self.list_input.focus_force()
        else:
            self.status_display.set_text("No entries found")
    
    def on_hide(self):
        """Called when the view is hidden"""
        logger.debug("ResultsListView: on_hide")
        self.results_view.clear()
    
    def focus(self):
        """Set focus to the list input for key handling"""
        if self.list_input:
            self.list_input.focus_force()
    
    def _handle_key(self, event):
        """Handle key presses for entry selection"""
        # Handle number key presses for direct selection
        if event.char.isdigit():
            index = int(event.char) - 1  # Convert to 0-based index
            if 0 <= index < len(self.current_entries):
                entry = self.current_entries[index]
                logger.debug(f"Direct selection via number key: {entry.title}")
                self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})
                if self.on_select:
                    self.on_select(entry)
            return "break"
        
        # Handle other character input - transition to search
        elif event.char.isprintable() and event.char not in [' ', '\t']:
            # Start new search with this character
            search_term = event.char
            logger.debug(f"Starting new search from results list: {search_term}")
            self.state_manager.transition_to(AppState.SEARCH, {'search_term': search_term})
            return "break"
        
        return None
    
    def _handle_return(self, event):
        """Handle return key"""
        current_highlight = self.results_view.get_current_highlight()
        
        if 0 <= current_highlight < len(self.current_entries):
            # Select highlighted entry
            entry = self.current_entries[current_highlight]
            logger.debug(f"Selecting highlighted entry: {entry.title}")
            self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})
            if self.on_select:
                self.on_select(entry)
        
        return "break"
    
    def _handle_arrow_up(self, event):
        """Handle up arrow key"""
        current_highlight = self.results_view.get_current_highlight()
        
        if current_highlight <= 0:
            # At first entry, go back to search mode
            self.state_manager.transition_to(AppState.SEARCH, {'search_term': ''})
        else:
            # Move highlight up
            entry = self.results_view.highlight_entry(current_highlight - 1)
        
        return "break"
    
    def _handle_arrow_down(self, event):
        """Handle down arrow key"""
        current_highlight = self.results_view.get_current_highlight()
        entry_count = self.results_view.get_entry_count()
        
        if current_highlight >= entry_count - 1:
            # At last entry, wrap to first
            entry = self.results_view.highlight_entry(0)
        else:
            # Move highlight down
            entry = self.results_view.highlight_entry(current_highlight + 1)
        
        return "break"
    
    def _handle_delete_key(self, event):
        """Handle delete key for recent entries"""
        if not self.is_recent_list:
            return "break"  # Only handle delete for recent entries
        
        current_highlight = self.results_view.get_current_highlight()
        if 0 <= current_highlight < len(self.current_entries):
            entry = self.current_entries[current_highlight]
            self._delete_recent_entry(entry)
        
        return "break"
    
    def _handle_escape(self, event):
        """Handle escape key"""
        # Go back to initial state or hide window
        if self.is_recent_list:
            self.state_manager.transition_to(AppState.INITIAL)
        else:
            # For search results, go back to search state
            self.state_manager.transition_to(AppState.SEARCH, {'search_term': ''})
        
        return "break"
    
    def _handle_backspace(self, event):
        """Handle backspace key"""
        # Go back to search mode
        self.state_manager.transition_to(AppState.SEARCH, {'search_term': ''})
        return "break"
    
    def _delete_recent_entry(self, entry):
        """Delete a recent entry"""
        if not self.window_relations_manager:
            logger.warning("Cannot delete recent entry: no window relations manager")
            return
        
        try:
            current_window_title = self.window_relations_manager.current_window_title
            if current_window_title and hasattr(entry, 'uuid'):
                entry_uuid = str(entry.uuid)
                logger.info(f"Deleting recent entry UUID '{entry_uuid}' for window '{current_window_title}'")
                self.window_relations_manager.remove_recent_entry(current_window_title, entry_uuid)
                
                # Refresh by going back to initial state
                self.state_manager.transition_to(AppState.INITIAL, {
                    'window_relations_manager': self.window_relations_manager
                })
            else:
                logger.warning("Cannot delete recent entry: missing window title or entry UUID")
        except Exception as e:
            logger.error(f"Error deleting recent entry: {e}")