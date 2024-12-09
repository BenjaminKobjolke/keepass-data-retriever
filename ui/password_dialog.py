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
        self.root.withdraw()  # Hide initially to prevent white flash
        
        # Configure window
        self.root.title(title)
        self.root.configure(bg=WindowManager.BG_COLOR)
        
        # Set theme before creating widgets
        self.root.tk_setPalette(
            background=WindowManager.BG_COLOR,
            foreground=WindowManager.FG_COLOR,
            activeBackground=WindowManager.BUTTON_BG,
            activeForeground=WindowManager.FG_COLOR
        )
        
        # Make it stay on top and set transparency
        self.root.attributes('-topmost', True, '-alpha', WindowManager.TRANSPARENCY)
        
        # Configure styles
        self.style = ttk.Style(self.root)
        self._configure_styles()
        
        # Create main frame with dark background
        self.frame = tk.Frame(self.root, bg=WindowManager.BG_COLOR, borderwidth=0, highlightthickness=0)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add password label
        self.label = tk.Label(
            self.frame,
            text="Enter KeePass password:",
            bg=WindowManager.BG_COLOR,
            fg=WindowManager.FG_COLOR,
            font=('Segoe UI', 11)
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
        
        # Bind enter key and escape key
        self.entry.bind('<Return>', lambda e: self._on_ok())
        self.root.bind('<Escape>', lambda e: self._on_cancel())
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Show window now that it's configured
        self.root.deiconify()
        
        # Focus the entry
        self.entry.focus_force()

    def _configure_styles(self):
        """Configure ttk styles for dark theme"""
        self.style.configure('TFrame',
            background=WindowManager.BG_COLOR
        )
        self.style.configure('TLabel',
            background=WindowManager.BG_COLOR,
            foreground=WindowManager.FG_COLOR,
            font=('Segoe UI', 11)
        )

    def _on_ok(self):
        """Handle OK button click"""
        self.password = self.entry.get()
        self.root.quit()
        self.root.destroy()

    def _on_cancel(self):
        """Handle cancel action"""
        self.password = None
        self.root.quit()
        self.root.destroy()

    def get_password(self):
        """Show dialog and return password"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Dialog error: {e}")
        finally:
            try:
                self.root.destroy()
            except:
                pass
        return self.password
