import tkinter as tk
from tkinter import ttk
from typing import List, Any

class ResultsView:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.entries_frame = ttk.Frame(self.frame)
        self.entries_frame.pack(fill=tk.X, padx=5, pady=5)

    def show_entries(self, entries: List[Any]):
        """Show list of entries"""
        # Clear previous entries
        self.clear()
        
        # Show entries
        for i, entry in enumerate(entries, 1):
            text = f"{i}. {entry.title}"
            if entry.username:
                text += f" ({entry.username})"
            if entry.url:
                text += f"\n   {entry.url}"
            
            label = ttk.Label(self.entries_frame, text=text, wraplength=280)
            label.pack(fill=tk.X, padx=5, pady=2)
        
        # Show the frame
        self.frame.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        """Clear all entries"""
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        self.frame.pack_forget()

    def hide(self):
        """Hide the results view"""
        self.frame.pack_forget()
