"""Theme management for the application UI."""

from tkinter import ttk


class ThemeManager:
    """Manages application theme colors and TTK styles."""

    # Dark theme colors
    BG_COLOR = '#1e1e1e'  # Dark background
    FG_COLOR = '#ffffff'  # White text
    ENTRY_BG = '#2d2d2d'  # Slightly lighter for inputs
    ENTRY_FG = '#ffffff'  # White text for inputs
    BUTTON_BG = '#3d3d3d'  # Even lighter for buttons
    BUTTON_FG = '#ffffff'  # White text for buttons
    TRANSPARENCY = 0.9

    @staticmethod
    def configure_styles(style: ttk.Style):
        """
        Configure TTK styles for dark theme.

        Args:
            style: TTK Style object to configure
        """
        # Frame style
        style.configure('Dark.TFrame',
            background=ThemeManager.BG_COLOR
        )

        # Label style
        style.configure('Dark.TLabel',
            background=ThemeManager.BG_COLOR,
            foreground=ThemeManager.FG_COLOR,
            font=('Segoe UI', 11)  # Larger font
        )

        # Entry style
        style.configure('Dark.TEntry',
            fieldbackground=ThemeManager.ENTRY_BG,
            foreground=ThemeManager.FG_COLOR,
            insertcolor=ThemeManager.FG_COLOR,
            borderwidth=1,
            relief='solid',
            font=('Segoe UI', 11)  # Larger font
        )
        style.map('Dark.TEntry',
            fieldbackground=[('focus', ThemeManager.ENTRY_BG)],
            foreground=[('focus', ThemeManager.FG_COLOR)]
        )

        # Button style
        style.configure('Dark.TButton',
            background=ThemeManager.BUTTON_BG,
            foreground=ThemeManager.FG_COLOR,
            borderwidth=1,
            relief='solid',
            font=('Segoe UI', 11)  # Larger font
        )
        style.map('Dark.TButton',
            background=[('active', ThemeManager.ENTRY_BG)],
            foreground=[('active', ThemeManager.FG_COLOR)]
        )
