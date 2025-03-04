import tkinter as tk

class DarkEntry(tk.Entry):
    """Custom Entry widget with dark theme styling"""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'background': '#2d2d2d',  # Dark input background
            'foreground': '#ffffff',  # White text
            'insertbackground': '#ffffff',  # White cursor
            'highlightthickness': 1,  # Border thickness
            'highlightbackground': '#1e1e1e',  # Border color when not focused
            'highlightcolor': '#3d3d3d',  # Border color when focused
            'relief': 'flat',  # Flat appearance
            'font': ('Segoe UI', 16)  # Increased font size
        })
        super().__init__(*args, **kwargs)
