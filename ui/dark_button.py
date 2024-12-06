import tkinter as tk

class DarkButton(tk.Button):
    """Custom Button widget with dark theme styling"""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'background': '#3d3d3d',  # Dark button background
            'foreground': '#ffffff',  # White text
            'activebackground': '#4d4d4d',  # Lighter when pressed
            'activeforeground': '#ffffff',  # White text when pressed
            'font': ('Segoe UI', 11),  # Larger font
            'relief': 'flat',  # Flat appearance
            'borderwidth': 1,  # Thin border
            'highlightthickness': 0  # No highlight border
        })
        super().__init__(*args, **kwargs)
        
        # Bind hover events for visual feedback
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, e):
        """Mouse enter event"""
        self['background'] = '#4d4d4d'

    def _on_leave(self, e):
        """Mouse leave event"""
        self['background'] = '#3d3d3d'
