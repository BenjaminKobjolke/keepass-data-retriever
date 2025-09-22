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

class InitialView(BaseView):
    """Initial view showing recent entries for the current window"""
    
    def __init__(self, parent: tk.Widget, state_manager, view_manager):
        self.on_search: Callable = None
        self.on_get_recent_entries: Callable = None
        self.on_select: Callable = None
        self.window_relations_manager = None
        
        # UI components
        self.search_input = None
        self.status_display = None
        self.results_view = None
        
        super().__init__(parent, state_manager, view_manager)
    
    def set_callbacks(self, on_search: Callable, on_get_recent_entries: Callable, 
                     on_select: Callable, window_relations_manager):
        """Set callback functions for this view"""
        self.on_search = on_search
        self.on_get_recent_entries = on_get_recent_entries
        self.on_select = on_select
        self.window_relations_manager = window_relations_manager
    
    def get_supported_states(self) -> List[AppState]:
        """Return list of application states this view supports"""
        return [AppState.INITIAL]
    
    def create_ui(self):
        """Create the UI elements for initial view"""
        # Create search input
        input_frame = ttk.Frame(self.container, style='Dark.TFrame')
        input_frame.pack(padx=2, pady=2)
        
        self.search_input = DarkEntry(input_frame, width=40)
        self.search_input.pack()
        
        # Bind events
        self.search_input.bind('<Return>', self._handle_search)
        self.search_input.bind('<Up>', self._handle_arrow_up)
        self.search_input.bind('<Down>', self._handle_arrow_down)
        self.search_input.bind('<Delete>', self._handle_delete_key)
        self.search_input.bind('<Escape>', self._handle_escape)
        
        # Create status display
        self.status_display = StatusDisplay(self.container)
        
        # Create results view
        self.results_view = ResultsView(self.container, self.state_manager)
    
    def on_show(self, data: Dict[str, Any]):
        """Called when the view is shown"""
        logger.debug("InitialView: on_show")
        
        # Clear search input
        self.search_input.delete(0, tk.END)
        
        # Get window relations manager from data
        self.window_relations_manager = data.get('window_relations_manager')
        
        # Load and show recent entries
        if self.on_get_recent_entries and self.window_relations_manager:
            try:
                recent_entries = self.on_get_recent_entries()
                if recent_entries:
                    logger.debug(f"Showing {len(recent_entries)} recent entries")
                    self.results_view.show_entries(recent_entries, is_recent_list=True)
                    self.status_display.set_text("Recent entries for this window:")
                    # Ensure search input has focus for keyboard navigation
                    self.search_input.focus_force()
                else:
                    logger.debug("No recent entries found")
                    self.status_display.set_text("No recent entries. Start typing to search.")
                    self.search_input.focus_force()
            except Exception as e:
                logger.error(f"Error loading recent entries: {e}")
                self.status_display.set_text("Start typing to search.")
                self.search_input.focus_force()
        else:
            self.status_display.set_text("Start typing to search.")
            self.search_input.focus_force()
    
    def on_hide(self):
        """Called when the view is hidden"""
        logger.debug("InitialView: on_hide")
        self.results_view.clear()
    
    def focus(self):
        """Set focus to the search input"""
        if self.search_input:
            self.search_input.focus_force()
    
    def _handle_search(self, event):
        """Handle search input"""
        search_term = self.search_input.get().strip()
        if search_term:
            # Check for exit command
            if search_term.lower() == '/exit':
                self.view_manager.parent.quit()
                return "break"

            # Check for reload command
            if search_term.lower() == '/reload':
                if hasattr(self.view_manager, '_handle_reload') and self.view_manager._handle_reload:
                    self.view_manager._handle_reload()
                return "break"
            
            logger.debug(f"Search initiated: {search_term}")
            # Transition to search state
            self.state_manager.transition_to(AppState.SEARCH, {'search_term': search_term})
            if self.on_search:
                self.on_search(search_term)
        return "break"
    
    def _handle_arrow_up(self, event):
        """Handle up arrow key"""
        # If we have results, start navigating them
        if self.results_view.get_entry_count() > 0:
            # Highlight last entry
            entry = self.results_view.highlight_entry(self.results_view.get_entry_count() - 1)
            if entry:
                self._transition_to_results_navigation()
        return "break"
    
    def _handle_arrow_down(self, event):
        """Handle down arrow key"""
        # If we have results, start navigating them
        if self.results_view.get_entry_count() > 0:
            # Highlight first entry
            entry = self.results_view.highlight_entry(0)
            if entry:
                self._transition_to_results_navigation()
        return "break"
    
    def _handle_delete_key(self, event):
        """Handle delete key for recent entries"""
        current_highlight = self.results_view.get_current_highlight()
        if current_highlight >= 0:
            entry_details = self.results_view.get_current_highlighted_entry_details()
            if entry_details and entry_details.get('is_recent', False):
                entry = entry_details['entry']
                self._delete_recent_entry(entry)
        return "break"
    
    def _handle_escape(self, event):
        """Handle escape key"""
        self.view_manager.hide_current_view()  # Hide the window
        return "break"
    
    def _transition_to_results_navigation(self):
        """Transition to results list view for navigation"""
        entries = [details['entry'] for details in self.results_view.entry_frames]
        self.state_manager.transition_to(AppState.RESULTS_LIST, {
            'entries': entries,
            'is_recent_list': True
        })
    
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
                
                # Refresh the view
                self.on_show({'window_relations_manager': self.window_relations_manager})
            else:
                logger.warning("Cannot delete recent entry: missing window title or entry UUID")
        except Exception as e:
            logger.error(f"Error deleting recent entry: {e}")