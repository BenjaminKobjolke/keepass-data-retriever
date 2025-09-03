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

class SearchView(BaseView):
    """View for active search input with live results"""
    
    def __init__(self, parent: tk.Widget, state_manager, view_manager):
        self.on_search: Callable = None
        self.on_select: Callable = None
        
        # UI components
        self.search_input = None
        self.status_display = None
        self.results_view = None
        
        # Search state
        self.current_entries = []
        self.search_term = ""
        
        super().__init__(parent, state_manager, view_manager)
    
    def set_callbacks(self, on_search: Callable, on_select: Callable):
        """Set callback functions for this view"""
        self.on_search = on_search
        self.on_select = on_select
    
    def get_supported_states(self) -> List[AppState]:
        """Return list of application states this view supports"""
        return [AppState.SEARCH]
    
    def create_ui(self):
        """Create the UI elements for search view"""
        # Create search input
        input_frame = ttk.Frame(self.container, style='Dark.TFrame')
        input_frame.pack(padx=2, pady=2)
        
        self.search_input = DarkEntry(input_frame, width=40)
        self.search_input.pack()
        
        # Bind events
        self.search_input.bind('<Return>', self._handle_return)
        self.search_input.bind('<Up>', self._handle_arrow_up)
        self.search_input.bind('<Down>', self._handle_arrow_down)
        self.search_input.bind('<Escape>', self._handle_escape)
        self.search_input.bind('<BackSpace>', self._handle_backspace)
        
        # Create status display
        self.status_display = StatusDisplay(self.container)
        
        # Create results view
        self.results_view = ResultsView(self.container, self.state_manager)
    
    def on_show(self, data: Dict[str, Any]):
        """Called when the view is shown"""
        logger.debug("SearchView: on_show")
        
        # Set search term from data
        self.search_term = data.get('search_term', '')
        if self.search_term:
            self.search_input.delete(0, tk.END)
            self.search_input.insert(0, self.search_term)
            # Position cursor at end
            self.search_input.icursor(tk.END)
        
        # Show search results if available
        entries = data.get('entries', [])
        if entries:
            self.show_search_results(entries)
        else:
            self.status_display.set_text("Searching...")
    
    def on_hide(self):
        """Called when the view is hidden"""
        logger.debug("SearchView: on_hide")
        self.results_view.clear()
    
    def focus(self):
        """Set focus to the search input"""
        if self.search_input:
            self.search_input.focus_force()
    
    def show_search_results(self, entries: List[Any]):
        """Show search results"""
        self.current_entries = entries
        
        if not entries:
            self.results_view.clear()
            self.status_display.set_text("No entries found")
            return
        
        # Show results
        self.results_view.show_entries(entries, is_recent_list=False)
        self.status_display.show_search_results(entries)
        
        # Ensure results are visible by making sure the frame is packed
        if hasattr(self.results_view, 'frame'):
            self.results_view.frame.pack(fill=tk.BOTH, expand=True)
        
        # Ensure search input has focus for keyboard navigation
        self.search_input.focus_force()
        
        # If single result, we could auto-select it or keep in search mode
        # For now, keeping search mode active as specified
        logger.debug(f"Showing {len(entries)} search results in SearchView")
    
    def _handle_return(self, event):
        """Handle return key"""
        current_highlight = self.results_view.get_current_highlight()
        
        if current_highlight >= 0 and current_highlight < len(self.current_entries):
            # Select highlighted entry
            entry = self.current_entries[current_highlight]
            logger.debug(f"Selecting entry from search: {entry.title}")
            self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})
            if self.on_select:
                self.on_select(entry)
        else:
            # Perform new search or repeat current search
            search_term = self.search_input.get().strip()
            if search_term:
                # Check for exit command
                if search_term.lower() == '/exit':
                    self.parent.quit()
                    return "break"
                
                logger.debug(f"New search from SearchView: {search_term}")
                self.search_term = search_term
                if self.on_search:
                    self.on_search(search_term)
        
        return "break"
    
    def _handle_arrow_up(self, event):
        """Handle up arrow key"""
        if self.results_view.get_entry_count() > 0:
            current_highlight = self.results_view.get_current_highlight()
            
            # If no highlight or at first entry, clear highlight and focus search
            if current_highlight <= 0:
                # Clear highlight by setting to -1 and refreshing display
                self.results_view.current_highlight = -1
                # Clear all highlights using the proper method
                if len(self.results_view.entry_frames) > 0:
                    # Force clear all highlights by re-highlighting -1 (which clears all)
                    for i in range(len(self.results_view.entry_frames)):
                        entry_details = self.results_view.entry_frames[i]
                        frame = entry_details['frame']
                        is_recent = entry_details['is_recent']
                        # Reset to default style
                        frame.configure(style='RecentEntry.TFrame' if is_recent else 'Dark.TFrame')
                        for child in frame.winfo_children():
                            if isinstance(child, ttk.Label):
                                if child.cget('font') == ('Segoe UI', 10):
                                    child.configure(style='RecentEntryURL.TLabel' if is_recent else 'Dark.TLabel')
                                else:
                                    child.configure(style='RecentEntry.TLabel' if is_recent else 'Dark.TLabel')
                self.search_input.focus_force()
            else:
                # Move highlight up
                entry = self.results_view.highlight_entry(current_highlight - 1)
        
        return "break"
    
    def _handle_arrow_down(self, event):
        """Handle down arrow key"""
        if self.results_view.get_entry_count() > 0:
            current_highlight = self.results_view.get_current_highlight()
            
            if current_highlight < 0:
                # No current highlight, highlight first entry
                entry = self.results_view.highlight_entry(0)
            else:
                # Move highlight down (with wrapping)
                new_index = (current_highlight + 1) % self.results_view.get_entry_count()
                entry = self.results_view.highlight_entry(new_index)
        
        return "break"
    
    def _handle_escape(self, event):
        """Handle escape key"""
        # Clear search or hide window
        if self.search_input.get().strip():
            # Clear search input and go back to initial state
            self.search_input.delete(0, tk.END)
            self.state_manager.transition_to(AppState.INITIAL)
        else:
            # Hide window
            self.view_manager.hide_current_view()
        
        return "break"
    
    def _handle_backspace(self, event):
        """Handle backspace key"""
        # If search input becomes empty after backspace, transition to initial state
        current_text = self.search_input.get()
        if len(current_text) <= 1:  # Will be empty after backspace
            # Schedule transition to initial state after the backspace is processed
            self.search_input.after(1, lambda: self.state_manager.transition_to(AppState.INITIAL))
        
        return None  # Allow normal backspace processing