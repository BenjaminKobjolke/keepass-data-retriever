"""Window positioning service for calculating and validating window positions."""

import tkinter as tk
import win32gui
import win32con
import win32api
from config import config


class WindowPositioningService:
    """Handles window positioning strategies and validation."""

    @staticmethod
    def validate_position(x: int, y: int, width: int, height: int) -> tuple[int, int]:
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

    @staticmethod
    def position_at_mouse(root: tk.Tk, width: int, height: int):
        """
        Position window near mouse cursor with offset.

        Args:
            root: Tkinter root window
            width: Window width
            height: Window height
        """
        mouse_x = root.winfo_pointerx()
        mouse_y = root.winfo_pointery()

        offset_x = 20
        offset_y = 20

        # Calculate initial position
        x = mouse_x + offset_x
        y = mouse_y + offset_y

        # Validate position to ensure window is visible on screen
        x, y = WindowPositioningService.validate_position(x, y, width, height)

        # Set window position
        root.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def position_center_window(root: tk.Tk, width: int, height: int):
        """
        Position window in center of active window.

        Args:
            root: Tkinter root window
            width: Window width
            height: Window height
        """
        try:
            # Get active window handle
            active_hwnd = win32gui.GetForegroundWindow()

            # Get active window rect
            left, top, right, bottom = win32gui.GetWindowRect(active_hwnd)
            active_width = right - left
            active_height = bottom - top

            # Calculate center position
            center_x = left + (active_width - width) // 2
            center_y = top + (active_height - height) // 2

            # Validate position to ensure window is visible on screen (all edges)
            center_x, center_y = WindowPositioningService.validate_position(center_x, center_y, width, height)

            # Set window position
            root.geometry(f"{width}x{height}+{center_x}+{center_y}")
        except Exception as e:
            # Fallback to mouse position if error
            print(f"Error positioning window in center: {e}")
            WindowPositioningService.position_at_mouse(root, width, height)

    @staticmethod
    def position_center_screen(root: tk.Tk, width: int, height: int):
        """
        Position window in center of screen.

        Args:
            root: Tkinter root window
            width: Window width
            height: Window height
        """
        try:
            # Get screen dimensions
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

            # Calculate center position
            center_x = (screen_width - width) // 2
            center_y = (screen_height - height) // 2

            # Validate position to ensure window is visible on screen
            center_x, center_y = WindowPositioningService.validate_position(center_x, center_y, width, height)

            # Set window position
            root.geometry(f"{width}x{height}+{center_x}+{center_y}")
        except Exception as e:
            # Fallback to mouse position if error
            print(f"Error positioning window in center of screen: {e}")
            WindowPositioningService.position_at_mouse(root, width, height)

    @staticmethod
    def position_window(root: tk.Tk, width: int, height: int, mode: str = None):
        """
        Position window based on configuration mode.

        Args:
            root: Tkinter root window
            width: Window width
            height: Window height
            mode: Optional positioning mode override (mouse, center, center_screen)
        """
        # Get window position mode from config if not specified
        if mode is None:
            mode = config.get_window_position_mode()

        if mode == 'center':
            # Center in active window
            WindowPositioningService.position_center_window(root, width, height)
        elif mode == 'center_screen':
            # Center on screen
            WindowPositioningService.position_center_screen(root, width, height)
        else:
            # Default: position at mouse cursor
            WindowPositioningService.position_at_mouse(root, width, height)
