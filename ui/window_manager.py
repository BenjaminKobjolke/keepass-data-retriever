import tkinter as tk
from tkinter import ttk
import win32gui
import win32api
import win32con
from .theme_manager import ThemeManager
from .window_positioning_service import WindowPositioningService
from .window_focus_manager import WindowFocusManager
from config import config
from .logger import Logger

logger = Logger.get_instance()


class WindowManager:
    # Window sizes
    WINDOW_WIDTH = config.get_window_width()
    WINDOW_HEIGHT_NORMAL = 121  # Increased to fit mode indicator
    MAX_WINDOW_HEIGHT = 800

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
        self._auto_resize_id = None

        # Configure window
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", ThemeManager.TRANSPARENCY)
        self.root.configure(bg=ThemeManager.BG_COLOR)

        # Configure styles using ThemeManager
        self.style = ttk.Style()
        ThemeManager.configure_styles(self.style)

        # Create main frame
        self.main_frame = ttk.Frame(self.root, style="Dark.TFrame")
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
        self.root.bind("<Button-3>", lambda e: self.menu.post(e.x_root, e.y_root))

    def show(self):
        """Show the window"""
        # Reset expanded state; expansion happens via set_expanded after content is loaded
        self.window_expanded = False
        window_width = self.WINDOW_WIDTH
        window_height = self.WINDOW_HEIGHT_NORMAL
        WindowPositioningService.position_window(self.root, window_width, window_height)

        # Force focus
        self.focus_manager.force_focus()

        # Start focus monitoring after 2 seconds
        logger.debug("Will start focus check in 2 seconds")
        self.root.after(
            2000, lambda: self.focus_manager.start_focus_monitoring(on_focus_lost=self.hide)
        )

    def hide(self):
        """Hide the window"""
        self.focus_manager.stop_focus_monitoring()
        self.root.withdraw()

    def quit(self):
        """Quit the application"""
        self.root.quit()

    def set_expanded(self, expanded: bool):
        """Set window expanded state"""
        if expanded and self.window_expanded:
            # Already expanded, skip redundant resize
            return

        self.window_expanded = expanded

        if not expanded:
            # Collapse to normal height
            window_width = self.WINDOW_WIDTH
            WindowPositioningService.position_window(
                self.root, window_width, self.WINDOW_HEIGHT_NORMAL
            )
        else:
            # Set a generous initial height, then auto-resize after content is laid out
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            try:
                screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
                initial_height = min(self.MAX_WINDOW_HEIGHT, screen_height - y - 40)
            except Exception:
                initial_height = self.MAX_WINDOW_HEIGHT
            self.root.geometry(f"{self.WINDOW_WIDTH}x{initial_height}+{x}+{y}")

    def auto_resize(self):
        """Schedule an auto-resize to fit content"""
        # Cancel any pending auto-resize
        if self._auto_resize_id is not None:
            self.root.after_cancel(self._auto_resize_id)
        self._auto_resize_id = self.root.after(10, self._do_auto_resize)

    def _do_auto_resize(self):
        """Resize window to fit content, clamped to screen bounds"""
        self._auto_resize_id = None
        if not self.window_expanded:
            return

        self.root.update_idletasks()
        req_height = self.root.winfo_reqheight()

        x = self.root.winfo_x()
        y = self.root.winfo_y()

        try:
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            max_h = min(self.MAX_WINDOW_HEIGHT, screen_height - y - 40)
        except Exception:
            max_h = self.MAX_WINDOW_HEIGHT

        height = max(self.WINDOW_HEIGHT_NORMAL, min(req_height, max_h))
        self.root.geometry(f"{self.WINDOW_WIDTH}x{height}+{x}+{y}")

    def get_main_frame(self) -> ttk.Frame:
        """Get the main frame for adding widgets"""
        return self.main_frame

    def check_focus(self, event=None) -> bool:
        """Legacy focus check method for compatibility"""
        return True
