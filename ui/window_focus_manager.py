"""Window focus management for forcing and monitoring focus."""

import tkinter as tk
import time
import win32gui
import win32con


class WindowFocusManager:
    """Manages window focus forcing and monitoring."""

    def __init__(self, root: tk.Tk, hwnd):
        """
        Initialize focus manager.

        Args:
            root: Tkinter root window
            hwnd: Windows window handle
        """
        self.root = root
        self.hwnd = hwnd
        self.focus_check_active = False
        self.on_focus_lost_callback = None

    def force_focus(self):
        """Force focus to the window using multiple methods."""
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

    def start_focus_monitoring(self, on_focus_lost=None):
        """
        Start monitoring window focus.

        Args:
            on_focus_lost: Callback function to call when focus is lost
        """
        print("Starting focus check")
        self.focus_check_active = True
        self.on_focus_lost_callback = on_focus_lost
        self._check_focus_timer()

    def stop_focus_monitoring(self):
        """Stop monitoring window focus."""
        self.focus_check_active = False

    def _check_focus_timer(self):
        """Periodically check if window has focus."""
        if not self.focus_check_active:
            return

        if self.root.winfo_ismapped() and self.hwnd:  # Only check if window is mapped
            # Get active window handle
            try:
                active_hwnd = win32gui.GetForegroundWindow()

                # Get window titles for debugging
                active_title = win32gui.GetWindowText(active_hwnd)
                our_title = win32gui.GetWindowText(self.hwnd)

                # Hide if active window is not our window
                if active_hwnd != self.hwnd:
                    print("Window lost focus")
                    if self.on_focus_lost_callback:
                        self.on_focus_lost_callback()
                    return  # Stop checking after window loses focus
            except Exception as e:
                print(f"Focus check error (non-critical): {e}")

        # Check every second
        self.root.after(1000, self._check_focus_timer)
