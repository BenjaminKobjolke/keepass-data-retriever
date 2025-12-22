"""Theme management for the application UI."""

from tkinter import ttk
from config import config


class ThemeManager:
    """Manages application theme colors and TTK styles."""

    # Preset themes
    PRESETS = {
        'dark': {
            'bg_color': '#1e1e1e',
            'fg_color': '#ffffff',
            'entry_bg': '#2d2d2d',
            'entry_fg': '#ffffff',
            'button_bg': '#3d3d3d',
            'button_fg': '#ffffff',
            'highlight_bg': '#2E2E2E',
            'recent_entry_bg': '#063970',
            'action_highlight_bg': '#5a5a5a',
            'button_hover_bg': '#4d4d4d',
            'transparency': 0.9
        },
        'light': {
            'bg_color': '#f0f0f0',
            'fg_color': '#000000',
            'entry_bg': '#ffffff',
            'entry_fg': '#000000',
            'button_bg': '#e0e0e0',
            'button_fg': '#000000',
            'highlight_bg': '#d0d0d0',
            'recent_entry_bg': '#b0c4de',
            'action_highlight_bg': '#c0c0c0',
            'button_hover_bg': '#d5d5d5',
            'transparency': 0.95
        }
    }

    # Default values (dark theme)
    _DEFAULTS = PRESETS['dark']

    # Cached color values
    _colors = None

    @classmethod
    def _load_colors(cls):
        """Load colors from config or use defaults"""
        if cls._colors is None:
            cls._colors = {}
            preset = config.get_theme_preset()

            if preset in ('dark', 'light'):
                # Use preset colors
                cls._colors = cls.PRESETS[preset].copy()
            else:
                # Custom - load from config
                cls._colors = config.get_all_theme_colors()
                cls._colors['transparency'] = config.get_theme_transparency()

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """Get a theme color by name"""
        cls._load_colors()
        return cls._colors.get(color_name, cls._DEFAULTS.get(color_name, '#1e1e1e'))

    @classmethod
    def get_transparency(cls) -> float:
        """Get theme transparency value"""
        cls._load_colors()
        return cls._colors.get('transparency', 0.9)

    @classmethod
    def reload_colors(cls):
        """Reload colors from config (call after settings change)"""
        cls._colors = None
        cls._load_colors()

    @classmethod
    def apply_preset(cls, preset_name: str):
        """Apply a preset theme"""
        if preset_name in cls.PRESETS:
            preset = cls.PRESETS[preset_name]
            config.set_theme_preset(preset_name)
            for name, value in preset.items():
                if name == 'transparency':
                    config.set_theme_transparency(value)
                else:
                    config.set_theme_color(name, value)
            cls.reload_colors()

    @classmethod
    def apply_custom_colors(cls, colors: dict, transparency: float = None):
        """Apply custom colors"""
        config.set_theme_preset('custom')
        config.set_all_theme_colors(colors)
        if transparency is not None:
            config.set_theme_transparency(transparency)
        cls.reload_colors()

    # Backward compatible class-level properties
    @classmethod
    @property
    def BG_COLOR(cls) -> str:
        return cls.get_color('bg_color')

    @classmethod
    @property
    def FG_COLOR(cls) -> str:
        return cls.get_color('fg_color')

    @classmethod
    @property
    def ENTRY_BG(cls) -> str:
        return cls.get_color('entry_bg')

    @classmethod
    @property
    def ENTRY_FG(cls) -> str:
        return cls.get_color('entry_fg')

    @classmethod
    @property
    def BUTTON_BG(cls) -> str:
        return cls.get_color('button_bg')

    @classmethod
    @property
    def BUTTON_FG(cls) -> str:
        return cls.get_color('button_fg')

    @classmethod
    @property
    def TRANSPARENCY(cls) -> float:
        return cls.get_transparency()

    @staticmethod
    def configure_styles(style: ttk.Style):
        """
        Configure TTK styles for dark theme.

        Args:
            style: TTK Style object to configure
        """
        # Frame style
        style.configure('Dark.TFrame',
            background=ThemeManager.get_color('bg_color')
        )

        # Label style
        style.configure('Dark.TLabel',
            background=ThemeManager.get_color('bg_color'),
            foreground=ThemeManager.get_color('fg_color'),
            font=('Segoe UI', 11)
        )

        # Entry style
        style.configure('Dark.TEntry',
            fieldbackground=ThemeManager.get_color('entry_bg'),
            foreground=ThemeManager.get_color('fg_color'),
            insertcolor=ThemeManager.get_color('fg_color'),
            borderwidth=1,
            relief='solid',
            font=('Segoe UI', 11)
        )
        style.map('Dark.TEntry',
            fieldbackground=[('focus', ThemeManager.get_color('entry_bg'))],
            foreground=[('focus', ThemeManager.get_color('fg_color'))]
        )

        # Button style
        style.configure('Dark.TButton',
            background=ThemeManager.get_color('button_bg'),
            foreground=ThemeManager.get_color('fg_color'),
            borderwidth=1,
            relief='solid',
            font=('Segoe UI', 11)
        )
        style.map('Dark.TButton',
            background=[('active', ThemeManager.get_color('entry_bg'))],
            foreground=[('active', ThemeManager.get_color('fg_color'))]
        )
