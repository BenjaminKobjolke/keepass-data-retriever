"""Highlight navigation handler for results view."""

from tkinter import ttk
from .logger import Logger

logger = Logger.get_instance()


class HighlightHandler:
    """Handles keyboard navigation and highlighting in results."""

    def __init__(self, results_view, input_manager, window_manager):
        self.results_view = results_view
        self.input_manager = input_manager
        self.window_manager = window_manager

    def handle_highlight_change(self, direction: str):
        """
        Navigate highlights in results view.

        Args:
            direction: 'up' or 'down'
        """
        current_index = self.results_view.get_current_highlight()
        entry_count = self.results_view.get_entry_count()

        if entry_count == 0:
            return

        # Special case: if on first entry and pressing up, deselect all entries
        if direction == "up" and current_index == 0:
            self._clear_all_highlights()
            return

        # Calculate new index based on direction
        if direction == "up":
            new_index = max(0, current_index - 1) if current_index >= 0 else entry_count - 1
        elif direction == "down":
            new_index = (current_index + 1) % entry_count if current_index >= 0 else 0
        else:
            return

        # Highlight the new entry and update current_entry
        entry = self.results_view.highlight_entry(new_index)
        if entry:
            self.input_manager.current_entry = entry

        # Ensure the window is expanded to show results
        self.window_manager.set_expanded(True)

    def _clear_all_highlights(self):
        """Clear all entry highlights and reset to search input."""
        # Clear highlight state
        self.results_view.current_highlight = -1
        self.input_manager.current_entry = None

        # Clear UI highlights
        for i in range(len(self.results_view.entry_frames)):
            frame = self.results_view.entry_frames[i]["frame"]
            frame.configure(style="Dark.TFrame")

            # Change style of all child labels
            for child in frame.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(style="Dark.TLabel")

        # Ensure focus is on the search input
        self.input_manager.search_input.focus_force()
