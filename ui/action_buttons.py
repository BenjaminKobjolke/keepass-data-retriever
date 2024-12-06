import tkinter as tk
from tkinter import ttk
from typing import Callable

class ActionButtons:
    def __init__(self, parent: ttk.Frame, on_action: Callable):
        self.frame = ttk.Frame(parent)
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
            btn = ttk.Button(
                self.frame,
                text=text,
                command=lambda a=action: self.on_action(a)
            )
            btn.pack(fill=tk.X, pady=1)

    def show(self):
        """Show action buttons"""
        self.frame.pack(fill=tk.X, padx=5, pady=5)

    def hide(self):
        """Hide action buttons"""
        self.frame.pack_forget()
