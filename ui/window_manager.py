import tkinter as tk
from tkinter import ttk
import win32gui
from .theme_manager import ThemeManager
from .window_positioning_service import WindowPositioningService
from .window_focus_manager import WindowFocusManager


class WindowManager:
    # Window sizes (adjusted for wider input)
    WINDOW_WIDTH = 420
    WINDOW_HEIGHT_NORMAL = 91
    WINDOW_HEIGHT_EXPANDED = 520

    # Re-export theme colors for backward compatibility
    BG_COLOR = ThemeManager.BG_COLOR
    FG_COLOR = ThemeManager.FG_COLOR
    ENTRY_BG = ThemeManager.ENTRY_BG
    ENTRY_FG = ThemeManager.ENTRY_FG
    BUTTON_BG = ThemeManager.BUTTON_BG
    BUTTON_FG = ThemeManager.BUTTON_FG
    TRANSPARENCY = ThemeManager.TRANSPARENCY

    # Re-export validation method for backward compatibility
    @staticmethod
    def validate_window_position(x: int, y: int, width: int, height: int) -> tuple[int, int]:
        """Validate window position (delegates to WindowPositioningService)."""
        return WindowPositioningService.validate_position(x, y, width, height)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.window_expanded = False

        # Configure window
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True, '-alpha', ThemeManager.TRANSPARENCY)
        self.root.configure(bg=ThemeManager.BG_COLOR)

        # Configure styles using ThemeManager
        self.style = ttk.Style()
        ThemeManager.configure_styles(self.style)

        # Create main frame
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)  # Reduced padding

        # Create system tray menu
        self._create_tray_menu()

        # Store our window handle
        self.hwnd = None
        self.root.update()  # Ensure window is created
        self.hwnd = win32gui.GetParent(self.root.winfo_id())

        # Initialize focus manager
        self.focus_manager = WindowFocusManager(self.root, self.hwnd)

        # Start minimized
        self.root.withdraw()

    def _create_tray_menu(self):
        """Create system tray menu"""
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Show", command=self.show)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.quit)

        # Bind right-click on root window to show menu
        self.root.bind('<Button-3>', lambda e: self.menu.post(e.x_root, e.y_root))

    def show(self):
        """Show the window"""
        # Position window
        window_width = self.WINDOW_WIDTH
        window_height = self.WINDOW_HEIGHT_EXPANDED if self.window_expanded else self.WINDOW_HEIGHT_NORMAL
        WindowPositioningService.position_window(self.root, window_width, window_height)

        # Force focus
        self.focus_manager.force_focus()

        # Start focus monitoring after 2 seconds
        print("Will start focus check in 2 seconds")
        self.root.after(2000, lambda: self.focus_manager.start_focus_monitoring(on_focus_lost=self.hide))

    def hide(self):
        """Hide the window"""
        self.focus_manager.stop_focus_monitoring()
        self.root.withdraw()

    def quit(self):
        """Quit the application"""
        self.root.quit()

    def set_expanded(self, expanded: bool):
        """Set window expanded state"""
        self.window_expanded = expanded
        # Re-position window with new dimensions
        window_width = self.WINDOW_WIDTH
        window_height = self.WINDOW_HEIGHT_EXPANDED if self.window_expanded else self.WINDOW_HEIGHT_NORMAL
        WindowPositioningService.position_window(self.root, window_width, window_height)

    def get_main_frame(self) -> ttk.Frame:
        """Get the main frame for adding widgets"""
        return self.main_frame

    def check_focus(self, event=None) -> bool:
        """Legacy focus check method for compatibility"""
        return True
