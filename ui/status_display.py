from tkinter import ttk
from .url_formatter import shorten_url
from config import config


class StatusDisplay:
    def __init__(self, parent: ttk.Frame):
        wraplength = config.get_window_width() - 60
        self.label = ttk.Label(
            parent,
            text="",
            wraplength=wraplength,
            style="Dark.TLabel",
            font=("Segoe UI", 11),  # Larger font
        )
        self.label.pack(padx=5, pady=(0, 5))

    def show_search_results(self, entries, single_entry=None):
        """Show search results status"""
        if not entries:
            self.set_text("No entries found")
            return

        if single_entry:
            text = f"{single_entry.title}"
            if single_entry.url:
                text += f"\nURL: {shorten_url(single_entry.url)}"
            self.set_text(text)
        else:
            self.set_text(f"Found {len(entries)} entries. Press 1-{len(entries)} to select.")

    def show_selected_entry(self, entry):
        """Show selected entry status"""
        text = f"Selected: {entry.title}"
        if entry.url:
            text += f"\nURL: {shorten_url(entry.url)}"
        self.set_text(text)

    def set_text(self, text: str):
        """Set status text"""
        self.label.configure(text=text)
