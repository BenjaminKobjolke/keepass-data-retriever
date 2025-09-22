from typing import Dict, Any, Optional, Type, List
import tkinter as tk
from .state_manager import StateManager, AppState
from .base_view import BaseView
from .logger import Logger

logger = Logger.get_instance()

class ViewManager:
    """Manages view lifecycle and transitions"""
    
    def __init__(self, parent: tk.Widget, state_manager: StateManager, handle_reload=None):
        self.parent = parent
        self.state_manager = state_manager
        self.views: Dict[str, BaseView] = {}
        self.active_view: Optional[BaseView] = None
        self.view_classes: Dict[str, Type[BaseView]] = {}
        self._handle_reload = handle_reload

        # Register as state listener
        self.state_manager.register_listener(self)
    
    def register_view(self, view_name: str, view_class: Type[BaseView]):
        """Register a view class for lazy instantiation"""
        self.view_classes[view_name] = view_class
        logger.debug(f"Registered view: {view_name}")
    
    def get_or_create_view(self, view_name: str) -> Optional[BaseView]:
        """Get existing view or create new one if it doesn't exist"""
        if view_name not in self.views:
            if view_name not in self.view_classes:
                logger.error(f"View class not registered: {view_name}")
                return None
            
            # Create new view instance
            view_class = self.view_classes[view_name]
            view = view_class(self.parent, self.state_manager, self)
            view.create_ui()
            self.views[view_name] = view
            logger.debug(f"Created new view instance: {view_name}")
        
        return self.views[view_name]
    
    def show_view(self, view_name: str, data: Dict[str, Any] = None):
        """Show a specific view, hiding the current one"""
        # Hide current view
        if self.active_view and self.active_view.is_active:
            self.active_view.hide()
        
        # Get or create the new view
        new_view = self.get_or_create_view(view_name)
        if new_view:
            new_view.show(data)
            self.active_view = new_view
            logger.debug(f"Switched to view: {view_name}")
        else:
            logger.error(f"Failed to show view: {view_name}")
    
    def hide_current_view(self):
        """Hide the currently active view"""
        if self.active_view and self.active_view.is_active:
            self.active_view.hide()
            self.active_view = None
    
    def get_active_view(self) -> Optional[BaseView]:
        """Get the currently active view"""
        return self.active_view
    
    def get_view(self, view_name: str) -> Optional[BaseView]:
        """Get a view by name (returns None if not created yet)"""
        return self.views.get(view_name)
    
    def on_state_changed(self, state: AppState, data: Dict[str, Any]):
        """Handle state changes and route to appropriate view"""
        logger.debug(f"ViewManager: State changed to {state}")
        
        # Map states to view names
        state_to_view = {
            AppState.INITIAL: 'InitialView',
            AppState.SEARCH: 'SearchView',
            AppState.RESULTS_LIST: 'ResultsListView',
            AppState.ENTRY_ACTIONS: 'EntryDetailsView',
            AppState.HIDDEN: None
        }
        
        view_name = state_to_view.get(state)
        
        if view_name:
            self.show_view(view_name, data)
        elif state == AppState.HIDDEN:
            self.hide_current_view()
    
    def cleanup(self):
        """Clean up all views"""
        for view in self.views.values():
            view.cleanup()
        self.views.clear()
        
        if self.state_manager:
            self.state_manager.unregister_listener(self)