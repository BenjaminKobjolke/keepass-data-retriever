import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

class WindowManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.window_expanded = False
        
        # Configure window
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='white')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create system tray menu
        self._create_tray_menu()

    def _create_tray_menu(self):
        """Create system tray menu"""
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Show", command=self.show)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.quit)
        
        # Bind right-click on root window to show menu
        self.root.bind('<Button-3>', lambda e: self.menu.post(e.x_root, e.y_root))

    def _position_window(self):
        """Position window near mouse cursor"""
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        
        offset_x = 20
        offset_y = 20
        
        if self.window_expanded:
            self.root.geometry(f"300x400+{mouse_x + offset_x}+{mouse_y + offset_y}")
        else:
            self.root.geometry(f"300x70+{mouse_x + offset_x}+{mouse_y + offset_y}")

    def show(self):
        """Show the window"""
        self._position_window()
        self.root.deiconify()

    def hide(self):
        """Hide the window"""
        self.root.withdraw()

    def quit(self):
        """Quit the application"""
        self.root.quit()

    def set_expanded(self, expanded: bool):
        """Set window expanded state"""
        self.window_expanded = expanded
        self._position_window()

    def get_main_frame(self) -> ttk.Frame:
        """Get the main frame for adding widgets"""
        return self.main_frame

    def check_focus(self, event: Optional[tk.Event] = None) -> bool:
        """Check if window should be hidden when focus is lost"""
        current_focus = self.root.focus_get()
        print(f"Focus changed to: {current_focus}")
        
        # Only hide if focus is completely lost from our window
        if not current_focus or not str(current_focus).startswith(str(self.root)):
            print("Focus lost from window")
            self.hide()
            return True
        return False
