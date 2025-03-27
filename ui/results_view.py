import tkinter as tk
from tkinter import ttk
from typing import List, Any, Dict
from .state_manager import StateManager, AppState
from .logger import Logger

# Get logger instance
logger = Logger.get_instance()

class ResultsView:
    # Define colors for highlighting
    HIGHLIGHT_BG = '#4a4a4a'  # Much lighter than background for better visibility
    
    def __init__(self, parent, state_manager: StateManager = None):
        # Configure styles for highlighting
        self.style = ttk.Style()
        self._configure_highlight_styles()
        
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.entries_frame = ttk.Frame(self.frame, style='Dark.TFrame')
        self.entries_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Store entry frames for easy access
        self.entry_frames = []
        self.current_highlight = -1
        
        # Store state manager
        self.state_manager = state_manager
        
        # Register as state listener if state manager is provided
        if self.state_manager:
            self.state_manager.register_listener(self)
    
    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"ResultsView: State changed to {state}")
        
        if state == AppState.INITIAL:
            # Clear results when transitioning to initial state
            self.clear()
        elif state == AppState.RESULTS_LIST:
            # Don't show entries here - let SearchWindow handle it
            # This prevents duplicate entries
            pass
        elif state == AppState.ENTRY_ACTIONS:
            # Clear results when transitioning to entry actions state
            # (the selected entry will be shown by SearchWindow)
            self.clear()
        elif state == AppState.HIDDEN:
            # Hide results when transitioning to hidden state
            self.hide()
        
    def _configure_highlight_styles(self):
        """Configure styles for highlighted entries"""
        # Get the background color from the Dark.TFrame style
        bg_color = self.style.lookup('Dark.TFrame', 'background')
        fg_color = self.style.lookup('Dark.TLabel', 'foreground')
        
        # Create highlighted frame style
        self.style.configure('Highlighted.TFrame', 
            background=self.HIGHLIGHT_BG
        )
        
        # Create highlighted label style
        self.style.configure('Highlighted.TLabel',
            background=self.HIGHLIGHT_BG,
            foreground=fg_color,
            font=('Segoe UI', 11)
        )
        
        # Create highlighted URL label style
        self.style.configure('HighlightedURL.TLabel',
            background=self.HIGHLIGHT_BG,
            foreground=fg_color,
            font=('Segoe UI', 10)
        )

    def show_entries(self, entries: List[Any]):
        """Show list of entries"""
        # Clear previous entries
        self.clear()
        
        # Reset entry frames list and highlight index
        self.entry_frames = []
        self.current_highlight = -1
        
        # Show entries
        for i, entry in enumerate(entries, 1):
            # Create frame for each entry
            entry_frame = ttk.Frame(self.entries_frame, style='Dark.TFrame')
            entry_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Store the frame and associated entry
            self.entry_frames.append({
                'frame': entry_frame,
                'entry': entry,
                'index': i - 1  # Store zero-based index
            })
            
            # Title and username
            title_text = f"{i}. {entry.title}"
            if entry.username:
                title_text += f" ({entry.username})"
            
            title_label = ttk.Label(
                entry_frame,
                text=title_text,
                wraplength=360,  # Increased for larger window
                style='Dark.TLabel',
                font=('Segoe UI', 11)  # Larger font
            )
            title_label.pack(fill=tk.X, anchor='w')
            
            # URL on next line if present
            if entry.url:
                url_label = ttk.Label(
                    entry_frame,
                    text=f"   {entry.url}",
                    wraplength=360,  # Increased for larger window
                    style='Dark.TLabel',
                    font=('Segoe UI', 10)  # Slightly smaller for URL
                )
                url_label.pack(fill=tk.X, anchor='w')
        
        # Show the frame
        self.frame.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        """Clear all entries"""
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        self.frame.pack_forget()
        self.entry_frames = []
        self.current_highlight = -1

    def hide(self):
        """Hide the results view"""
        self.frame.pack_forget()
        # Reset highlight when hiding
        self.current_highlight = -1
        
    def highlight_entry(self, index: int) -> Any:
        """Highlight the entry at the given index and return the entry object"""
        if not self.entry_frames or index < 0 or index >= len(self.entry_frames):
            return None
            
        # Clear previous highlight if any
        if self.current_highlight >= 0 and self.current_highlight < len(self.entry_frames):
            prev_frame = self.entry_frames[self.current_highlight]['frame']
            prev_frame.configure(style='Dark.TFrame')
            
            # Change style of all child labels
            for child in prev_frame.winfo_children():
                if isinstance(child, ttk.Label):
                    # Check if it's a URL label (smaller font)
                    if child.cget('font') == ('Segoe UI', 10):
                        child.configure(style='Dark.TLabel')
                    else:
                        child.configure(style='Dark.TLabel')
        
        # Set new highlight
        self.current_highlight = index
        current_frame = self.entry_frames[index]['frame']
        current_frame.configure(style='Highlighted.TFrame')
        
        # Change style of all child labels
        for child in current_frame.winfo_children():
            if isinstance(child, ttk.Label):
                # Check if it's a URL label (smaller font)
                if child.cget('font') == ('Segoe UI', 10):
                    child.configure(style='HighlightedURL.TLabel')
                else:
                    child.configure(style='Highlighted.TLabel')
                
        # Return the entry object
        return self.entry_frames[index]['entry']
        
    def get_current_highlight(self) -> int:
        """Get the index of the currently highlighted entry"""
        return self.current_highlight
        
    def get_entry_count(self) -> int:
        """Get the number of entries"""
        return len(self.entry_frames)
