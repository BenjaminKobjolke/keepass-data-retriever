import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import win32gui
import win32con
import win32api
import time
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class WindowManager:
    # Dark theme colors
    BG_COLOR = '#1e1e1e'  # Dark background
    FG_COLOR = '#ffffff'  # White text
    ENTRY_BG = '#2d2d2d'  # Slightly lighter for inputs
    ENTRY_FG = '#ffffff'  # White text for inputs
    BUTTON_BG = '#3d3d3d'  # Even lighter for buttons
    BUTTON_FG = '#ffffff'  # White text for buttons
    TRANSPARENCY = 0.9

    # Window sizes (adjusted for wider input)
    WINDOW_WIDTH = 420
    WINDOW_HEIGHT_NORMAL = 91
    WINDOW_HEIGHT_EXPANDED = 520

    @staticmethod
    def validate_window_position(x: int, y: int, width: int, height: int) -> tuple[int, int]:
        """
        Validate and clamp window position to ensure it's visible on screen.

        Args:
            x: Window x position
            y: Window y position
            width: Window width
            height: Window height

        Returns:
            Tuple of (validated_x, validated_y) coordinates
        """
        try:
            # Get screen dimensions using win32api (more reliable than tkinter)
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

            # Clamp x to ensure window is visible horizontally
            # Left edge: ensure x >= 0
            # Right edge: ensure x + width <= screen_width
            validated_x = max(0, min(x, screen_width - width))

            # Clamp y to ensure window is visible vertically
            # Top edge: ensure y >= 0
            # Bottom edge: ensure y + height <= screen_height
            validated_y = max(0, min(y, screen_height - height))

            return (validated_x, validated_y)
        except Exception as e:
            print(f"Error validating window position: {e}")
            # Return original coordinates if validation fails
            return (x, y)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.window_expanded = False
        self.focus_check_active = False
        
        # Configure window
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True, '-alpha', self.TRANSPARENCY)
        self.root.configure(bg=self.BG_COLOR)
        
        # Configure styles
        self.style = ttk.Style()
        self._configure_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)  # Reduced padding
        
        # Create system tray menu
        self._create_tray_menu()
        
        # Store our window handle
        self.hwnd = None
        self.root.update()  # Ensure window is created
        self.hwnd = win32gui.GetParent(self.root.winfo_id())
        
        # Start minimized
        self.root.withdraw()

    def _configure_styles(self):
        """Configure ttk styles for dark theme"""
        # Frame style
        self.style.configure('Dark.TFrame', 
            background=self.BG_COLOR
        )
        
        # Label style
        self.style.configure('Dark.TLabel',
            background=self.BG_COLOR,
            foreground=self.FG_COLOR,
            font=('Segoe UI', 11)  # Larger font
        )
        
        # Entry style
        self.style.configure('Dark.TEntry',
            fieldbackground=self.ENTRY_BG,
            foreground=self.FG_COLOR,
            insertcolor=self.FG_COLOR,
            borderwidth=1,
            relief='solid',
            font=('Segoe UI', 11)  # Larger font
        )
        self.style.map('Dark.TEntry',
            fieldbackground=[('focus', self.ENTRY_BG)],
            foreground=[('focus', self.FG_COLOR)]
        )
        
        # Button style
        self.style.configure('Dark.TButton',
            background=self.BUTTON_BG,
            foreground=self.FG_COLOR,
            borderwidth=1,
            relief='solid',
            font=('Segoe UI', 11)  # Larger font
        )
        self.style.map('Dark.TButton',
            background=[('active', self.ENTRY_BG)],
            foreground=[('active', self.FG_COLOR)]
        )

    def _create_tray_menu(self):
        """Create system tray menu"""
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Show", command=self.show)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.quit)
        
        # Bind right-click on root window to show menu
        self.root.bind('<Button-3>', lambda e: self.menu.post(e.x_root, e.y_root))

    def _position_window_center_screen(self):
        """Position window in center of screen"""
        try:
            # Get screen dimensions
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

            # Calculate center position
            window_width = self.WINDOW_WIDTH
            window_height = self.WINDOW_HEIGHT_EXPANDED if self.window_expanded else self.WINDOW_HEIGHT_NORMAL

            center_x = (screen_width - window_width) // 2
            center_y = (screen_height - window_height) // 2

            # Validate position to ensure window is visible on screen
            center_x, center_y = self.validate_window_position(center_x, center_y, window_width, window_height)

            # Set window position
            self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        except Exception as e:
            # Fallback to mouse position if error
            print(f"Error positioning window in center of screen: {e}")
            self._position_window_mouse()
    
    def _position_window(self):
        """Position window based on settings"""
        # Get window position mode from config
        position_mode = config.get_window_position_mode()
        
        if position_mode == 'center':
            # Center in active window
            self._position_window_center()
        elif position_mode == 'center_screen':
            # Center on screen
            self._position_window_center_screen()
        else:
            # Default: position at mouse cursor
            self._position_window_mouse()
    
    def _position_window_mouse(self):
        """Position window near mouse cursor"""
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()

        offset_x = 20
        offset_y = 20

        # Calculate initial position
        x = mouse_x + offset_x
        y = mouse_y + offset_y

        # Determine window dimensions
        window_width = self.WINDOW_WIDTH
        window_height = self.WINDOW_HEIGHT_EXPANDED if self.window_expanded else self.WINDOW_HEIGHT_NORMAL

        # Validate position to ensure window is visible on screen
        x, y = self.validate_window_position(x, y, window_width, window_height)

        # Set window position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _position_window_center(self):
        """Position window in center of active window"""
        try:
            # Get active window handle
            active_hwnd = win32gui.GetForegroundWindow()

            # Get active window rect
            left, top, right, bottom = win32gui.GetWindowRect(active_hwnd)
            active_width = right - left
            active_height = bottom - top

            # Calculate center position
            window_width = self.WINDOW_WIDTH
            window_height = self.WINDOW_HEIGHT_EXPANDED if self.window_expanded else self.WINDOW_HEIGHT_NORMAL

            center_x = left + (active_width - window_width) // 2
            center_y = top + (active_height - window_height) // 2

            # Validate position to ensure window is visible on screen (all edges)
            center_x, center_y = self.validate_window_position(center_x, center_y, window_width, window_height)

            # Set window position
            self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        except Exception as e:
            # Fallback to mouse position if error
            print(f"Error positioning window in center: {e}")
            self._position_window_mouse()

    def _force_focus(self):
        """Force focus to our window"""
        if not self.hwnd:
            return
            
        try:
            # Try multiple focus methods
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            
            # Use tkinter's update to process events
            self.root.update_idletasks()
            self.root.update()
            
            # Try to set foreground window
            try:
                win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
                win32gui.SetForegroundWindow(self.hwnd)
            except Exception as e:
                print(f"Win32 focus error (non-critical): {e}")
                
            # Give window time to get focus
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Focus error (non-critical): {e}")

    def _start_focus_check(self):
        """Start focus checking after delay"""
        print("Starting focus check")
        self.focus_check_active = True
        self._check_focus_timer()

    def _check_focus_timer(self):
        """Periodically check focus"""
        if not self.focus_check_active:
            return
            
        if self.root.winfo_ismapped() and self.hwnd:  # Only check if window is mapped
            # Get active window handle
            try:
                active_hwnd = win32gui.GetForegroundWindow()
                
                # Get window titles for debugging
                active_title = win32gui.GetWindowText(active_hwnd)
                our_title = win32gui.GetWindowText(self.hwnd)
                #p rint(f"Active window: {active_title} ({active_hwnd})")
                #p rint(f"Our window: {our_title} ({self.hwnd})")
                
                # Hide if active window is not our window
                if active_hwnd != self.hwnd:
                    print("Window lost focus")
                    self.hide()
                    return  # Stop checking after window is hidden
            except Exception as e:
                print(f"Focus check error (non-critical): {e}")
        
        # Check every second
        self.root.after(1000, self._check_focus_timer)

    def check_focus(self, event: Optional[tk.Event] = None) -> bool:
        """Legacy focus check method for compatibility"""
        return True

    def show(self):
        """Show the window"""
        self.focus_check_active = False  # Reset focus check
        self._position_window()
        self._force_focus()
        # Start focus check after 2 seconds
        print("Will start focus check in 2 seconds")
        self.root.after(2000, self._start_focus_check)

    def hide(self):
        """Hide the window"""
        self.focus_check_active = False  # Stop focus check
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
