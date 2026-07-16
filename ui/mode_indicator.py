"""Mode indicator widget showing current view mode."""

import tkinter as tk
from .constants import APP_NAME
from .theme_manager import ThemeManager


class ModeIndicator:
    """A label widget that displays the current view mode."""

    # Mode colors (bright, distinct colors for each mode)
    MODE_COLORS = {
        "RECENT": "#1e90ff",  # DodgerBlue - for recent entries
        "SEARCH": "#ff8c00",  # DarkOrange - for active search
        "RESULTS": "#32cd32",  # LimeGreen - for results navigation
        "ACTIONS": "#9932cc",  # DarkOrchid - for entry actions
    }

    def __init__(self, parent: tk.Widget, mode: str = ""):
        """
        Initialize the mode indicator.

        Args:
            parent: Parent widget
            mode: Initial mode text (e.g., "RECENT", "SEARCH", "RESULTS")
        """
        self.parent = parent
        self.current_mode = mode

        # Create frame to hold the label with background color
        self.frame = tk.Frame(parent, bg=self._get_mode_color(mode))
        self.frame.pack(padx=2, pady=(2, 0), fill="x")

        # Create label
        self.label = tk.Label(
            self.frame,
            text=mode,
            font=("Segoe UI", 11, "bold"),
            fg="#ffffff",
            bg=self._get_mode_color(mode),
            padx=12,
            pady=4,
        )
        self.label.pack(anchor="w")

    def _get_mode_color(self, mode: str) -> str:
        """Get the background color for a mode."""
        return self.MODE_COLORS.get(mode, ThemeManager.get_color("button_bg"))

    def set_mode(self, mode: str):
        """
        Update the displayed mode.

        Args:
            mode: Mode text to display
        """
        self.current_mode = mode
        color = self._get_mode_color(mode)
        self.label.configure(text=mode, bg=color)
        self.frame.configure(bg=color)
        # Window title mirrors the current page (visible when frames are enabled)
        self.frame.winfo_toplevel().title(f"{APP_NAME} - {mode.capitalize()}")

    def pack(self, **kwargs):
        """Pack the indicator frame."""
        if "fill" not in kwargs:
            kwargs["fill"] = "x"
        self.frame.pack(**kwargs)

    def pack_forget(self):
        """Hide the indicator."""
        self.frame.pack_forget()
