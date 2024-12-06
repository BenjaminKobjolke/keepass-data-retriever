import tkinter as tk
from tkinter import ttk
from typing import List, Any

class ResultsView:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style='Dark.TFrame')
        self.entries_frame = ttk.Frame(self.frame, style='Dark.TFrame')
        self.entries_frame.pack(fill=tk.X, padx=5, pady=5)

    def show_entries(self, entries: List[Any]):
        """Show list of entries"""
        # Clear previous entries
        self.clear()
        
        # Show entries
        for i, entry in enumerate(entries, 1):
            # Create frame for each entry
            entry_frame = ttk.Frame(self.entries_frame, style='Dark.TFrame')
            entry_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Title and username
            title_text = f"{i}. {entry.title}"
            if entry.username:
                title_text += f" ({entry.username})"
            
            title_label = ttk.Label(
                entry_frame,
                text=title_text,
                wraplength=360,  # Increased for larger window
                style='Dark.TLabel',
                font=('Segoe UI', 11)  # Larger font
            )
            title_label.pack(fill=tk.X, anchor='w')
            
            # URL on next line if present
            if entry.url:
                url_label = ttk.Label(
                    entry_frame,
                    text=f"   {entry.url}",
                    wraplength=360,  # Increased for larger window
                    style='Dark.TLabel',
                    font=('Segoe UI', 10)  # Slightly smaller for URL
                )
                url_label.pack(fill=tk.X, anchor='w')
        
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
