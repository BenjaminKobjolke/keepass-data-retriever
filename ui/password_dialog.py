import tkinter as tk
from tkinter import ttk
from .dark_entry import DarkEntry
from .dark_button import DarkButton
from .window_manager import WindowManager

class PasswordDialog:
    def __init__(self, title="Enter KeePass Password"):
        self.password = None
        
        # Create dialog window
        self.root = tk.Tk()
        self.root.title(title)
        
        # Configure dark theme for the entire window
        self.root.configure(bg=WindowManager.BG_COLOR)
        self.root.option_add('*TFrame*background', WindowManager.BG_COLOR)
        self.root.option_add('*TLabel*background', WindowManager.BG_COLOR)
        self.root.option_add('*TLabel*foreground', WindowManager.FG_COLOR)
        
        # Make it stay on top and set transparency
        self.root.attributes('-topmost', True, '-alpha', WindowManager.TRANSPARENCY)
        
        # Configure styles
        self.style = ttk.Style()
        self._configure_styles()
        
        # Create outer frame to ensure dark background
        self.outer_frame = tk.Frame(self.root, bg=WindowManager.BG_COLOR)
        self.outer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create main frame
        self.frame = ttk.Frame(self.outer_frame, style='Dark.TFrame')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add password label
        self.label = ttk.Label(
            self.frame,
            text="Enter KeePass password:",
            style='Dark.TLabel'
        )
        self.label.pack(pady=(0, 5))
        
        # Add password entry
        self.entry = DarkEntry(self.frame, show="*")
        self.entry.pack(fill=tk.X, pady=(0, 10))
        
        # Add OK button using DarkButton
        self.button = DarkButton(
            self.frame,
            text="OK",
            command=self._on_ok
        )
        self.button.pack()
        
        # Bind enter key
        self.entry.bind('<Return>', lambda e: self._on_ok())
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Focus the entry
        self.entry.focus()

    def _configure_styles(self):
        """Configure ttk styles for dark theme"""
        # Frame style
        self.style.configure('Dark.TFrame',
            background=WindowManager.BG_COLOR
        )
        
        # Label style
        self.style.configure('Dark.TLabel',
            background=WindowManager.BG_COLOR,
            foreground=WindowManager.FG_COLOR,
            font=('Segoe UI', 11)
        )

    def _on_ok(self):
        """Handle OK button click"""
        self.password = self.entry.get()
        self.root.quit()
        self.root.destroy()

    def get_password(self):
        """Show dialog and return password"""
        self.root.mainloop()
        return self.password
