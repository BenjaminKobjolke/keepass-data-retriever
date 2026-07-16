import tkinter as tk
from tkinter import ttk
from typing import Callable, Tuple, Optional
import win32api
import win32con
from .constants import APP_NAME
from .dark_entry import DarkEntry
from .dark_button import DarkButton
from .window_manager import WindowManager, apply_frame_preference
from .logger import Logger

logger = Logger.get_instance()


class PasswordDialog:
    def __init__(
        self,
        title=f"{APP_NAME} - Enter Password",
        validator: Callable[[str], Tuple[bool, Optional[str]]] = None,
        parent: Optional[tk.Tk] = None,
    ):
        self.password = None
        self.validator = validator  # Callback: (password) -> (success: bool, error_msg: str|None)
        self._parent = parent
        self._owns_root = parent is None

        # Create dialog window. Reuse the existing Tk root via Toplevel when a
        # parent is supplied; creating a second Tk() corrupts shared Tcl state.
        if parent is not None:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        self.root.withdraw()  # Hide initially to prevent white flash
        apply_frame_preference(self.root)

        # Configure window
        self.root.title(title)
        self.root.configure(bg=WindowManager.BG_COLOR)

        # Set theme before creating widgets
        self.root.tk_setPalette(
            background=WindowManager.BG_COLOR,
            foreground=WindowManager.FG_COLOR,
            activeBackground=WindowManager.BUTTON_BG,
            activeForeground=WindowManager.FG_COLOR,
        )

        # Make it stay on top and set transparency
        self.root.attributes("-topmost", True, "-alpha", WindowManager.TRANSPARENCY)

        # Configure styles
        self.style = ttk.Style(self.root)
        self._configure_styles()

        # Create main frame with dark background
        self.frame = tk.Frame(
            self.root, bg=WindowManager.BG_COLOR, borderwidth=0, highlightthickness=0
        )
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add password label
        self.label = tk.Label(
            self.frame,
            text="Enter KeePass password:",
            bg=WindowManager.BG_COLOR,
            fg=WindowManager.FG_COLOR,
            font=("Segoe UI", 11),
        )
        self.label.pack(pady=(0, 5))

        # Add password entry
        self.entry = DarkEntry(self.frame, show="*")
        self.entry.pack(fill=tk.X, pady=(0, 5))

        # Add error label (initially hidden)
        self.error_label = tk.Label(
            self.frame,
            text="",
            bg=WindowManager.BG_COLOR,
            fg="#ff6b6b",  # Red error color matching dark theme
            font=("Segoe UI", 10),
            wraplength=280,
        )
        # Don't pack yet - will be shown when error occurs

        # Clear error when user starts typing
        self.entry.bind("<Key>", lambda e: self._hide_error())

        # Add OK button using DarkButton
        self.button = DarkButton(self.frame, text="OK", command=self._on_ok)
        self.button.pack()

        # Bind enter key and escape key
        self.entry.bind("<Return>", lambda e: self._on_ok())
        self.root.bind("<Escape>", lambda e: self._on_cancel())

        # Center the window
        self._center_window()

        # Show window now that it's configured
        self.root.deiconify()

        # Modal behavior when parented to existing Tk root.
        # Skip transient(): on Windows, a transient whose master is withdrawn
        # is auto-hidden by the window manager, which would close this dialog
        # before user can interact.
        if self._parent is not None:
            try:
                self.root.grab_set()
            except tk.TclError:
                pass

        # Treat window-close button the same as Esc
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Focus the entry
        self.entry.focus_force()

    def _center_window(self):
        """Center the window on the current screen with bounds validation"""
        self.root.update_idletasks()

        # Get window dimensions
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Get current screen dimensions using win32api (more reliable than tkinter after resolution changes)
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        # Calculate center position
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Validate position to ensure window is visible on screen
        x, y = WindowManager.validate_window_position(x, y, width, height)

        # Apply the geometry
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_styles(self):
        """Configure ttk styles for dark theme"""
        self.style.configure("TFrame", background=WindowManager.BG_COLOR)
        self.style.configure(
            "TLabel",
            background=WindowManager.BG_COLOR,
            foreground=WindowManager.FG_COLOR,
            font=("Segoe UI", 11),
        )

    def _on_ok(self):
        """Handle OK button click with optional validation"""
        password = self.entry.get()

        if self.validator:
            # Disable button and show "Checking..." state
            self.button.configure(state="disabled", text="Checking...")
            self.root.update()

            try:
                success, error_msg = self.validator(password)

                if success:
                    self.password = password
                    self._close()
                else:
                    # Show error and allow retry
                    self._show_error(error_msg or "Invalid password")
                    self.button.configure(state="normal", text="OK")
                    self.entry.delete(0, tk.END)
                    self.entry.focus_force()
            except Exception as e:
                self._show_error(f"Error: {str(e)}")
                self.button.configure(state="normal", text="OK")
                self.entry.delete(0, tk.END)
                self.entry.focus_force()
        else:
            # No validator - just return password (backward compatibility)
            self.password = password
            self._close()

    def _on_cancel(self):
        """Handle cancel action"""
        self.password = None
        self._close()

    def _close(self):
        """Close dialog. Must not call quit() when parented (would stop the
        parent's mainloop)."""
        try:
            if self._parent is not None:
                try:
                    self.root.grab_release()
                except tk.TclError:
                    pass
                self.root.destroy()
            else:
                self.root.quit()
                self.root.destroy()
        except tk.TclError:
            pass  # Already destroyed

    def _show_error(self, message: str):
        """Show error message below password field"""
        self.error_label.configure(text=message)
        self.error_label.pack(pady=(0, 5))
        # Flash the entry border red briefly
        self.entry.configure(highlightbackground="#ff6b6b", highlightcolor="#ff6b6b")
        self.root.after(2000, self._reset_entry_border)
        # Re-center window to accommodate error label
        self.root.update_idletasks()
        self._center_window()

    def _hide_error(self):
        """Hide error message"""
        if self.error_label.winfo_ismapped():
            self.error_label.pack_forget()
            self.error_label.configure(text="")

    def _reset_entry_border(self):
        """Reset entry border to default color"""
        try:
            self.entry.configure(highlightbackground="#1e1e1e", highlightcolor="#3d3d3d")
        except tk.TclError:
            pass  # Widget may have been destroyed

    def get_password(self):
        """Show dialog and return password"""
        try:
            # Re-center window right before showing in case resolution changed
            self._center_window()
            if self._parent is not None:
                # Parent's mainloop is already running; block until this dialog closes
                self._parent.wait_window(self.root)
            else:
                self.root.mainloop()
                try:
                    self.root.destroy()
                except tk.TclError:
                    pass
        except Exception as e:
            logger.error(f"Dialog error: {e}")
        return self.password
