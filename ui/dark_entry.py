import tkinter as tk
from .theme_manager import ThemeManager


class DarkEntry(tk.Entry):
    """Custom Entry widget with dark theme styling"""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'background': ThemeManager.get_color('entry_bg'),
            'foreground': ThemeManager.get_color('entry_fg'),
            'insertbackground': ThemeManager.get_color('entry_fg'),
            'highlightthickness': 1,
            'highlightbackground': ThemeManager.get_color('bg_color'),
            'highlightcolor': ThemeManager.get_color('button_bg'),
            'relief': 'flat',
            'font': ('Segoe UI', 16)
        })
        super().__init__(*args, **kwargs)

    def update_theme(self):
        """Update colors from current theme"""
        self.configure(
            background=ThemeManager.get_color('entry_bg'),
            foreground=ThemeManager.get_color('entry_fg'),
            insertbackground=ThemeManager.get_color('entry_fg'),
            highlightbackground=ThemeManager.get_color('bg_color'),
            highlightcolor=ThemeManager.get_color('button_bg')
        )
