"""Settings window for configuring application themes."""

import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Callable, Dict, Optional
from .theme_manager import ThemeManager
from .dark_button import DarkButton
from config import config


class SettingsWindow:
    """Settings window for configuring application themes."""

    # Color key to display label mapping
    COLOR_LABELS = {
        'bg_color': 'Background',
        'fg_color': 'Text',
        'entry_bg': 'Input Background',
        'entry_fg': 'Input Text',
        'button_bg': 'Button Background',
        'button_fg': 'Button Text',
        'highlight_bg': 'Highlight',
        'recent_entry_bg': 'Recent Entry',
        'action_highlight_bg': 'Action Highlight',
        'button_hover_bg': 'Button Hover',
    }

    def __init__(self, on_close: Callable = None, on_apply: Callable = None):
        """
        Initialize settings window.

        Args:
            on_close: Callback when window is closed
            on_apply: Callback when settings are applied
        """
        self.on_close = on_close
        self.on_apply = on_apply
        self.color_values: Dict[str, str] = {}
        self.color_previews: Dict[str, tk.Label] = {}
        self.transparency_value = 0.9

        # Create window
        self.root = tk.Toplevel()
        self.root.title("Settings - Theme Configuration")
        self.root.configure(bg=ThemeManager.get_color('bg_color'))
        self.root.attributes('-topmost', True)
        self.root.geometry("450x550")
        self.root.resizable(False, False)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._create_ui()
        self._load_current_colors()

        # Center window
        self._center_window()

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _create_ui(self):
        """Create the settings UI"""
        bg_color = ThemeManager.get_color('bg_color')
        fg_color = ThemeManager.get_color('fg_color')

        # Main frame
        main_frame = tk.Frame(self.root, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Theme Settings",
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 15))

        # Preset selection frame
        preset_frame = tk.Frame(main_frame, bg=bg_color)
        preset_frame.pack(fill=tk.X, pady=(0, 15))

        preset_label = tk.Label(
            preset_frame,
            text="Preset:",
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 11)
        )
        preset_label.pack(side=tk.LEFT)

        self.preset_var = tk.StringVar(value=config.get_theme_preset())
        preset_options = ['dark', 'light', 'custom']

        self.preset_menu = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=preset_options,
            state='readonly',
            width=15
        )
        self.preset_menu.pack(side=tk.LEFT, padx=(10, 0))
        self.preset_menu.bind('<<ComboboxSelected>>', self._on_preset_change)

        # Scrollable colors frame
        colors_container = tk.Frame(main_frame, bg=bg_color)
        colors_container.pack(fill=tk.BOTH, expand=True)

        # Canvas for scrolling
        canvas = tk.Canvas(colors_container, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(colors_container, orient="vertical", command=canvas.yview)
        self.colors_frame = tk.Frame(canvas, bg=bg_color)

        self.colors_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.colors_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create color rows
        for color_key, label in self.COLOR_LABELS.items():
            self._create_color_row(self.colors_frame, label, color_key)

        # Transparency slider
        transparency_frame = tk.Frame(main_frame, bg=bg_color)
        transparency_frame.pack(fill=tk.X, pady=(15, 0))

        trans_label = tk.Label(
            transparency_frame,
            text="Transparency:",
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 11)
        )
        trans_label.pack(side=tk.LEFT)

        self.transparency_var = tk.DoubleVar(value=ThemeManager.get_transparency())
        self.transparency_scale = tk.Scale(
            transparency_frame,
            from_=0.5,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.transparency_var,
            bg=bg_color,
            fg=fg_color,
            highlightthickness=0,
            troughcolor=ThemeManager.get_color('entry_bg'),
            length=200
        )
        self.transparency_scale.pack(side=tk.LEFT, padx=(10, 0))

        self.trans_value_label = tk.Label(
            transparency_frame,
            text=f"{self.transparency_var.get():.0%}",
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 10),
            width=5
        )
        self.trans_value_label.pack(side=tk.LEFT, padx=(5, 0))

        self.transparency_var.trace_add('write', self._on_transparency_change)

        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=bg_color)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        # Reset button
        reset_btn = DarkButton(
            buttons_frame,
            text="Reset to Default",
            command=self._reset_to_defaults
        )
        reset_btn.pack(side=tk.LEFT)

        # Cancel button
        cancel_btn = DarkButton(
            buttons_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT)

        # Save button
        save_btn = DarkButton(
            buttons_frame,
            text="Save & Close",
            command=self._save_and_close
        )
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # Apply button
        apply_btn = DarkButton(
            buttons_frame,
            text="Apply",
            command=self._apply_colors
        )
        apply_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def _create_color_row(self, parent, label: str, color_key: str):
        """Create a row with label, color preview, and picker button"""
        bg_color = ThemeManager.get_color('bg_color')
        fg_color = ThemeManager.get_color('fg_color')

        row_frame = tk.Frame(parent, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=3)

        # Label
        lbl = tk.Label(
            row_frame,
            text=label,
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 10),
            width=15,
            anchor='w'
        )
        lbl.pack(side=tk.LEFT)

        # Color preview
        preview = tk.Label(
            row_frame,
            text="",
            bg=self.color_values.get(color_key, ThemeManager.get_color(color_key)),
            width=8,
            height=1,
            relief='solid',
            borderwidth=1
        )
        preview.pack(side=tk.LEFT, padx=(10, 0))
        self.color_previews[color_key] = preview

        # Hex value label
        hex_label = tk.Label(
            row_frame,
            text=self.color_values.get(color_key, ThemeManager.get_color(color_key)),
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 9),
            width=8
        )
        hex_label.pack(side=tk.LEFT, padx=(5, 0))

        # Store reference for updating
        preview.hex_label = hex_label

        # Pick button
        pick_btn = DarkButton(
            row_frame,
            text="Pick",
            command=lambda k=color_key: self._pick_color(k)
        )
        pick_btn.pack(side=tk.RIGHT)

    def _load_current_colors(self):
        """Load current theme colors into the UI"""
        preset = config.get_theme_preset()
        self.preset_var.set(preset)

        if preset in ThemeManager.PRESETS:
            colors = ThemeManager.PRESETS[preset]
        else:
            colors = config.get_all_theme_colors()

        for color_key in self.COLOR_LABELS.keys():
            color = colors.get(color_key, ThemeManager.get_color(color_key))
            self.color_values[color_key] = color
            if color_key in self.color_previews:
                self.color_previews[color_key].configure(bg=color)
                if hasattr(self.color_previews[color_key], 'hex_label'):
                    self.color_previews[color_key].hex_label.configure(text=color)

        self.transparency_value = colors.get('transparency', ThemeManager.get_transparency())
        if isinstance(self.transparency_value, str):
            self.transparency_value = float(self.transparency_value)
        self.transparency_var.set(self.transparency_value)

    def _pick_color(self, color_key: str):
        """Open color picker dialog"""
        current_color = self.color_values.get(color_key, ThemeManager.get_color(color_key))
        result = colorchooser.askcolor(color=current_color, title=f"Choose {self.COLOR_LABELS[color_key]} Color")

        if result[1]:  # User selected a color
            new_color = result[1]
            self.color_values[color_key] = new_color
            self.color_previews[color_key].configure(bg=new_color)
            if hasattr(self.color_previews[color_key], 'hex_label'):
                self.color_previews[color_key].hex_label.configure(text=new_color)

            # Switch to custom preset when user picks a color
            self.preset_var.set('custom')

    def _on_preset_change(self, event=None):
        """Handle preset selection change"""
        preset = self.preset_var.get()
        if preset in ThemeManager.PRESETS:
            colors = ThemeManager.PRESETS[preset]
            for color_key, color in colors.items():
                if color_key in self.COLOR_LABELS:
                    self.color_values[color_key] = color
                    if color_key in self.color_previews:
                        self.color_previews[color_key].configure(bg=color)
                        if hasattr(self.color_previews[color_key], 'hex_label'):
                            self.color_previews[color_key].hex_label.configure(text=color)
                elif color_key == 'transparency':
                    self.transparency_var.set(color)

    def _on_transparency_change(self, *args):
        """Handle transparency slider change"""
        value = self.transparency_var.get()
        self.trans_value_label.configure(text=f"{value:.0%}")
        self.transparency_value = value

    def _apply_colors(self):
        """Apply colors without closing"""
        preset = self.preset_var.get()

        if preset in ('dark', 'light'):
            ThemeManager.apply_preset(preset)
        else:
            ThemeManager.apply_custom_colors(self.color_values, self.transparency_value)

        config.save_config()

        if self.on_apply:
            self.on_apply()

    def _save_and_close(self):
        """Save colors to config and close"""
        self._apply_colors()
        self._close()

    def _reset_to_defaults(self):
        """Reset to default dark theme"""
        self.preset_var.set('dark')
        self._on_preset_change()

    def _on_cancel(self):
        """Cancel and close without saving"""
        self._close()

    def _close(self):
        """Close the window"""
        if self.on_close:
            self.on_close()
        try:
            self.root.destroy()
        except:
            pass
