import tkinter as tk
from tkinter import ttk
from typing import Callable
from .dark_button import DarkButton

class ActionButtons:
    def __init__(self, parent: ttk.Frame, on_action: Callable):
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.on_action = on_action
        self._create_buttons()

    def _create_buttons(self):
        """Create action buttons"""
        actions = [
            ("Copy Username (1)", "username"),
            ("Copy Password (2)", "password"),
            ("Copy URL (3)", "url"),
            ("Open URL (4)", "open_url")
        ]
        
        for text, action in actions:
            btn = DarkButton(
                self.frame,
                text=text,
                command=lambda a=action: self.on_action(a),
                width=30  # Make buttons wider
            )
            btn.pack(fill=tk.X, pady=2)  # Slightly more vertical spacing

    def show(self):
        """Show action buttons"""
        self.frame.pack(fill=tk.X, padx=5, pady=5)

    def hide(self):
        """Hide action buttons"""
        self.frame.pack_forget()
