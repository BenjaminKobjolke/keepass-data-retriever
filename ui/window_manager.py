import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import win32gui
import win32con
import time

class WindowManager:
    # Dark theme colors
    BG_COLOR = '#1e1e1e'  # Dark background
    FG_COLOR = '#ffffff'  # White text
    ENTRY_BG = '#2d2d2d'  # Slightly lighter for inputs
    ENTRY_FG = '#ffffff'  # White text for inputs
    BUTTON_BG = '#3d3d3d'  # Even lighter for buttons
    BUTTON_FG = '#ffffff'  # White text for buttons
    TRANSPARENCY = 0.9
    
    # Window sizes (increased by 30%)
    WINDOW_WIDTH = 390  # 300 * 1.3
    WINDOW_HEIGHT_NORMAL = 91  # 70 * 1.3
    WINDOW_HEIGHT_EXPANDED = 520  # 400 * 1.3

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
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)  # Slightly larger padding
        
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

    def _position_window(self):
        """Position window near mouse cursor"""
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        
        offset_x = 20
        offset_y = 20
        
        if self.window_expanded:
            self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT_EXPANDED}+{mouse_x + offset_x}+{mouse_y + offset_y}")
        else:
            self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT_NORMAL}+{mouse_x + offset_x}+{mouse_y + offset_y}")

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
                print(f"Active window: {active_title} ({active_hwnd})")
                print(f"Our window: {our_title} ({self.hwnd})")
                
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
