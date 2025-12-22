import tkinter as tk
from .theme_manager import ThemeManager


class DarkButton(tk.Button):
    """Custom Button widget with dark theme styling"""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'background': ThemeManager.get_color('button_bg'),
            'foreground': ThemeManager.get_color('button_fg'),
            'activebackground': ThemeManager.get_color('button_hover_bg'),
            'activeforeground': ThemeManager.get_color('button_fg'),
            'font': ('Segoe UI', 11),
            'relief': 'flat',
            'borderwidth': 1,
            'highlightthickness': 0
        })
        super().__init__(*args, **kwargs)

        # Store colors for hover events
        self._normal_bg = ThemeManager.get_color('button_bg')
        self._hover_bg = ThemeManager.get_color('button_hover_bg')

        # Bind hover events for visual feedback
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, e):
        """Mouse enter event"""
        self['background'] = self._hover_bg

    def _on_leave(self, e):
        """Mouse leave event"""
        self['background'] = self._normal_bg

    def update_theme(self):
        """Update colors from current theme"""
        self._normal_bg = ThemeManager.get_color('button_bg')
        self._hover_bg = ThemeManager.get_color('button_hover_bg')
        self.configure(
            background=self._normal_bg,
            foreground=ThemeManager.get_color('button_fg'),
            activebackground=self._hover_bg,
            activeforeground=ThemeManager.get_color('button_fg')
        )
