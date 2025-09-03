from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
import tkinter as tk
from tkinter import ttk
from .state_manager import StateManager, AppState
from .logger import Logger

logger = Logger.get_instance()

class BaseView(ABC):
    """Abstract base class for all views in the application"""
    
    def __init__(self, parent: tk.Widget, state_manager: StateManager, view_manager: 'ViewManager'):
        self.parent = parent
        self.state_manager = state_manager
        self.view_manager = view_manager
        self.is_active = False
        self.container = None
        
        # Create the main container for this view
        self._create_container()
        
        # Register as state listener
        self.state_manager.register_listener(self)
    
    def _create_container(self):
        """Create the main container frame for this view"""
        self.container = ttk.Frame(self.parent, style='Dark.TFrame')
    
    @abstractmethod
    def create_ui(self):
        """Create the UI elements for this view"""
        pass
    
    @abstractmethod
    def get_supported_states(self) -> List[AppState]:
        """Return list of application states this view supports"""
        pass
    
    def show(self, data: Dict[str, Any] = None):
        """Show this view"""
        if not self.is_active:
            logger.debug(f"Showing view: {self.__class__.__name__}")
            self.container.pack(fill=tk.BOTH, expand=True)
            self.is_active = True
            self.on_show(data or {})
    
    def hide(self):
        """Hide this view"""
        if self.is_active:
            logger.debug(f"Hiding view: {self.__class__.__name__}")
            self.container.pack_forget()
            self.is_active = False
            self.on_hide()
    
    def on_show(self, data: Dict[str, Any]):
        """Called when the view is shown - override in subclasses"""
        pass
    
    def on_hide(self):
        """Called when the view is hidden - override in subclasses"""
        pass
    
    def on_state_changed(self, state: AppState, data: Dict[str, Any]):
        """Handle state changes - default implementation checks if view supports the state"""
        if state in self.get_supported_states():
            if not self.is_active:
                self.view_manager.show_view(self.__class__.__name__, data)
        else:
            if self.is_active:
                self.hide()
    
    def cleanup(self):
        """Clean up resources when view is destroyed"""
        if self.state_manager:
            self.state_manager.unregister_listener(self)
        if self.container:
            self.container.destroy()
    
    def focus(self):
        """Set focus to this view's primary input element - override in subclasses"""
        pass