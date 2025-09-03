import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, List
from ..base_view import BaseView
from ..state_manager import AppState
from ..status_display import StatusDisplay
from ..dark_entry import DarkEntry
from ..action_buttons import ActionButtons
from ..entry_actions_handler import EntryActionsHandler
from ..logger import Logger

logger = Logger.get_instance()

class EntryDetailsView(BaseView):
    """View for showing selected entry details with action buttons"""
    
    def __init__(self, parent: tk.Widget, state_manager, view_manager):
        self.on_action: Callable = None
        self.window_relations_manager = None
        self.hide_callback: Callable = None
        
        # UI components
        self.action_input = None
        self.status_display = None
        self.action_buttons = None
        self.entry_actions_handler = None
        
        # Entry state
        self.current_entry = None
        
        super().__init__(parent, state_manager, view_manager)
    
    def set_callbacks(self, on_action: Callable, window_relations_manager, hide_callback: Callable):
        """Set callback functions for this view"""
        self.on_action = on_action
        self.window_relations_manager = window_relations_manager
        self.hide_callback = hide_callback
        
        # Initialize entry actions handler now that we have callbacks
        if not self.entry_actions_handler:
            self.entry_actions_handler = EntryActionsHandler(
                self.parent,  # root window
                self.container,
                self.state_manager,
                self._handle_action_callback,
                self.window_relations_manager,
                self._handle_hide_callback
            )
    
    def get_supported_states(self) -> List[AppState]:
        """Return list of application states this view supports"""
        return [AppState.ENTRY_ACTIONS]
    
    def create_ui(self):
        """Create the UI elements for entry details view"""
        # Create action input (hidden input for key handling)
        input_frame = ttk.Frame(self.container, style='Dark.TFrame')
        input_frame.pack(padx=2, pady=2)
        
        self.action_input = DarkEntry(input_frame, width=40)
        self.action_input.pack()
        
        # Bind events
        self.action_input.bind('<Key>', self._handle_key)
        self.action_input.bind('<Return>', self._handle_return)
        self.action_input.bind('<Up>', self._handle_arrow_up)
        self.action_input.bind('<Down>', self._handle_arrow_down)
        self.action_input.bind('<Escape>', self._handle_escape)
        self.action_input.bind('<BackSpace>', self._handle_backspace)
        
        # Create status display
        self.status_display = StatusDisplay(self.container)
        
        # Entry actions handler will be initialized when callbacks are set
    
    def on_show(self, data: Dict[str, Any]):
        """Called when the view is shown"""
        logger.debug("EntryDetailsView: on_show")
        
        # Get entry from data
        self.current_entry = data.get('entry')
        
        if self.current_entry:
            # Show entry details in status
            self.status_display.show_selected_entry(self.current_entry)
            
            # Ensure entry actions handler is created
            if not self.entry_actions_handler:
                self.entry_actions_handler = EntryActionsHandler(
                    self.parent,  # root window
                    self.container,
                    self.state_manager,
                    self._handle_action_callback,
                    self.window_relations_manager,
                    self._handle_hide_callback
                )
            
            # Show action buttons
            self.entry_actions_handler.show_selected_entry(self.current_entry)
            
            # Clear the input field (it's just for key handling)
            self.action_input.delete(0, tk.END)
            
            # Ensure action input has focus for keyboard navigation
            self.action_input.focus_force()
            
            # Highlight first action button for navigation
            if hasattr(self.entry_actions_handler, 'actions') and self.entry_actions_handler.actions:
                self.entry_actions_handler.actions.highlight_action(0)
        else:
            logger.warning("EntryDetailsView shown without entry data")
            self.status_display.set_text("No entry selected")
    
    def on_hide(self):
        """Called when the view is hidden"""
        logger.debug("EntryDetailsView: on_hide")
        if self.entry_actions_handler:
            self.entry_actions_handler.cleanup()
    
    def focus(self):
        """Set focus to the action input for key handling"""
        if self.action_input:
            self.action_input.focus_force()
    
    def _handle_key(self, event):
        """Handle key presses for action selection"""
        # Handle character input for new search
        if event.char.isprintable() and event.char not in [' ', '\t']:
            # Start new search with this character
            search_term = event.char
            logger.debug(f"Starting new search from entry details: {search_term}")
            self.state_manager.transition_to(AppState.SEARCH, {'search_term': search_term})
            return "break"
        
        return None
    
    def _handle_return(self, event):
        """Handle return key - perform auto-type action"""
        if self.current_entry:
            logger.debug("Auto-type action triggered from EntryDetailsView")
            self.entry_actions_handler.handle_return_key(self.current_entry)
        
        return "break"
    
    def _handle_arrow_up(self, event):
        """Handle up arrow key - navigate action buttons"""
        if self.entry_actions_handler:
            self.entry_actions_handler.handle_highlight_change('up')
        
        return "break"
    
    def _handle_arrow_down(self, event):
        """Handle down arrow key - navigate action buttons"""
        if self.entry_actions_handler:
            self.entry_actions_handler.handle_highlight_change('down')
        
        return "break"
    
    def _handle_escape(self, event):
        """Handle escape key - go back to previous state or hide"""
        previous_state = self.state_manager.get_previous_state()
        
        if previous_state == AppState.RESULTS_LIST:
            # Go back to results list
            previous_data = self.state_manager.get_previous_state_data()
            self.state_manager.transition_to(AppState.RESULTS_LIST, previous_data)
        elif previous_state == AppState.SEARCH:
            # Go back to search
            self.state_manager.transition_to(AppState.SEARCH, {'search_term': ''})
        else:
            # Go to initial state
            self.state_manager.transition_to(AppState.INITIAL)
        
        return "break"
    
    def _handle_backspace(self, event):
        """Handle backspace key - go back to search"""
        self.state_manager.transition_to(AppState.SEARCH, {'search_term': ''})
        return "break"
    
    def _handle_action_callback(self, action: str, entry=None):
        """Handle action callback from entry actions handler"""
        logger.debug(f"EntryDetailsView: Action callback '{action}' for entry: {entry or self.current_entry}")
        if self.on_action:
            self.on_action(action, entry or self.current_entry)
    
    def _handle_hide_callback(self):
        """Handle hide callback from entry actions handler"""
        if self.hide_callback:
            self.hide_callback()