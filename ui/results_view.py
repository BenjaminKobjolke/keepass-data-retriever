import tkinter as tk
from tkinter import ttk
from typing import List, Any, Dict, Optional
from .state_manager import StateManager, AppState
from .logger import Logger
from .url_formatter import shorten_url
from .theme_manager import ThemeManager
from .constants import Fonts, Styles
from config import config

# Get logger instance
logger = Logger.get_instance()


class ResultsView:
    @property
    def HIGHLIGHT_BG(self):
        return ThemeManager.get_color("highlight_bg")

    @property
    def RECENT_ENTRY_BG(self):
        return ThemeManager.get_color("recent_entry_bg")

    def __init__(self, parent, state_manager: StateManager = None):
        # Configure styles for highlighting
        self.style = ttk.Style()
        self._configure_highlight_styles()

        self.frame = ttk.Frame(parent, style="Dark.TFrame")

        # Label shown before recent entries list
        self.list_label = ttk.Label(self.frame, text="", style="Dark.TLabel", font=("Segoe UI", 10))

        # Canvas and scrollbar for scrollable list
        self.canvas = None
        self.canvas_container = None
        self.entries_frame = None

        # Store entry frames for easy access
        self.entry_frames = []
        self.current_highlight = -1

        # Store state manager
        self.state_manager = state_manager

        # Register as state listener if state manager is provided
        if self.state_manager:
            self.state_manager.register_listener(self)

    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"ResultsView: State changed to {state}")

        if state == AppState.INITIAL:
            # Clear results when transitioning to initial state
            self.clear()
        elif state == AppState.RESULTS_LIST:
            # Don't show entries here - let SearchWindow handle it
            # This prevents duplicate entries
            pass
        elif state == AppState.ENTRY_ACTIONS:
            # Clear results when transitioning to entry actions state
            # (the selected entry will be shown by SearchWindow)
            self.clear()
        elif state == AppState.HIDDEN:
            # Hide results when transitioning to hidden state
            self.hide()

    def _configure_highlight_styles(self):
        """Configure styles for highlighted entries"""
        # Get foreground color from existing style
        fg_color = self.style.lookup(Styles.DARK_LABEL, "foreground")

        # Create highlighted frame style
        self.style.configure(
            Styles.HIGHLIGHTED_FRAME, background=self.HIGHLIGHT_BG, relief="solid", borderwidth=1
        )

        # Create highlighted label style
        self.style.configure(
            Styles.HIGHLIGHTED_LABEL,
            background=self.HIGHLIGHT_BG,
            foreground=fg_color,
            font=Fonts.NORMAL,
        )

        # Create highlighted URL label style
        self.style.configure(
            Styles.HIGHLIGHTED_URL_LABEL,
            background=self.HIGHLIGHT_BG,
            foreground=fg_color,
            font=Fonts.SMALL,
        )

        # Styles for recent entries
        self.style.configure(Styles.RECENT_ENTRY_FRAME, background=self.RECENT_ENTRY_BG)
        self.style.configure(
            Styles.RECENT_ENTRY_LABEL,
            background=self.RECENT_ENTRY_BG,
            foreground=fg_color,
            font=Fonts.NORMAL,
        )
        self.style.configure(
            Styles.RECENT_ENTRY_URL_LABEL,
            background=self.RECENT_ENTRY_BG,
            foreground=fg_color,
            font=Fonts.SMALL,
        )

        # Styles for highlighted recent entries
        self.style.configure(Styles.HIGHLIGHTED_RECENT_FRAME, background=self.HIGHLIGHT_BG)
        self.style.configure(
            Styles.HIGHLIGHTED_RECENT_LABEL,
            background=self.HIGHLIGHT_BG,
            foreground=fg_color,
            font=Fonts.NORMAL,
        )
        self.style.configure(
            Styles.HIGHLIGHTED_RECENT_URL_LABEL,
            background=self.HIGHLIGHT_BG,
            foreground=fg_color,
            font=Fonts.SMALL,
        )

    def show_entries(self, entries: List[Any], is_recent_list: bool = False):
        """Show list of entries"""
        wraplength = config.get_window_width() - 60

        # Clear previous entries
        self.clear()

        # Reset entry frames list and highlight index
        self.entry_frames = []
        self.current_highlight = -1

        # Show/hide the list label
        if is_recent_list:
            self.list_label.configure(text="Recent entries:")
            self.list_label.pack(fill=tk.X, padx=10, pady=(5, 0))
        else:
            self.list_label.pack_forget()

        # Create canvas container for scrollable list
        self.canvas_container = ttk.Frame(self.frame, style="Dark.TFrame")
        self.canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create canvas with dark-styled scrollbar
        bg_color = ThemeManager.get_color("bg_color")
        trough_color = ThemeManager.get_color("entry_bg")
        thumb_color = ThemeManager.get_color("button_bg")

        self.canvas = tk.Canvas(self.canvas_container, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            self.canvas_container,
            orient="vertical",
            command=self.canvas.yview,
            bg=thumb_color,
            troughcolor=trough_color,
            activebackground=ThemeManager.get_color("button_hover_bg"),
            highlightthickness=0,
            bd=0,
        )

        # Create entries frame inside canvas
        self.entries_frame = ttk.Frame(self.canvas, style="Dark.TFrame")

        # Bind Configure to update scroll region
        self.entries_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Add frame to canvas
        self.canvas.create_window((0, 0), window=self.entries_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse wheel events
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.entries_frame.bind("<MouseWheel>", self._on_mousewheel)

        base_frame_style = "RecentEntry.TFrame" if is_recent_list else "Dark.TFrame"
        base_label_style = "RecentEntry.TLabel" if is_recent_list else "Dark.TLabel"
        base_url_label_style = (
            "RecentEntryURL.TLabel" if is_recent_list else "Dark.TLabel"
        )  # DarkURL.TLabel if defined

        # Show entries
        for i, entry in enumerate(entries, 1):
            # Create frame for each entry
            entry_frame = ttk.Frame(self.entries_frame, style=base_frame_style)
            entry_frame.pack(fill=tk.X, padx=5, pady=3)

            # Store the frame and associated entry
            self.entry_frames.append(
                {
                    "frame": entry_frame,
                    "entry": entry,
                    "index": i - 1,  # Store zero-based index
                    "is_recent": is_recent_list,
                }
            )

            # Title and username
            title_text = f"{i}. {entry.title}"
            if entry.username:
                title_text += f" ({entry.username})"

            title_label = ttk.Label(
                entry_frame,
                text=title_text,
                wraplength=wraplength,
                style=base_label_style,
                font=("Segoe UI", 11),  # Larger font
            )
            title_label.pack(fill=tk.X, anchor="w")

            # URL on next line if present
            if entry.url:
                url_label = ttk.Label(
                    entry_frame,
                    text=f"   {shorten_url(entry.url)}",
                    wraplength=wraplength,
                    style=base_url_label_style,
                    font=("Segoe UI", 10),  # Slightly smaller for URL
                )
                url_label.pack(fill=tk.X, anchor="w")

            # Bind click event to the frame and its children
            entry_frame.bind("<Button-1>", lambda e, entry=entry: self._on_entry_click(entry))
            entry_frame.bind("<MouseWheel>", self._on_mousewheel)
            for child in entry_frame.winfo_children():
                child.bind("<Button-1>", lambda e, entry=entry: self._on_entry_click(entry))
                child.bind("<MouseWheel>", self._on_mousewheel)

        # Show the frame
        self.frame.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        """Clear all entries"""
        # Destroy canvas container (includes canvas, scrollbar, entries_frame)
        if self.canvas_container:
            self.canvas_container.destroy()
            self.canvas_container = None
            self.canvas = None
            self.entries_frame = None

        self.list_label.pack_forget()
        self.frame.pack_forget()
        self.entry_frames = []
        self.current_highlight = -1

    def hide(self):
        """Hide the results view"""
        self.frame.pack_forget()
        # Reset highlight when hiding
        self.current_highlight = -1

    def highlight_entry(self, index: int) -> Any:
        """Highlight the entry at the given index and return the entry object"""
        if not self.entry_frames or index < 0 or index >= len(self.entry_frames):
            return None

        # Clear previous highlight if any
        if 0 <= self.current_highlight < len(self.entry_frames):
            prev_details = self.entry_frames[self.current_highlight]
            prev_frame = prev_details["frame"]
            is_prev_recent = prev_details["is_recent"]

            prev_frame.configure(
                style=Styles.RECENT_ENTRY_FRAME if is_prev_recent else Styles.DARK_FRAME
            )
            for child in prev_frame.winfo_children():
                if isinstance(child, ttk.Label):
                    if child.cget("font") == Fonts.SMALL:
                        child.configure(
                            style=Styles.RECENT_ENTRY_URL_LABEL
                            if is_prev_recent
                            else Styles.DARK_LABEL
                        )
                    else:
                        child.configure(
                            style=Styles.RECENT_ENTRY_LABEL if is_prev_recent else Styles.DARK_LABEL
                        )

        # Set new highlight
        self.current_highlight = index
        current_details = self.entry_frames[index]
        current_frame = current_details["frame"]
        is_current_recent = current_details["is_recent"]

        current_frame.configure(
            style=Styles.HIGHLIGHTED_RECENT_FRAME if is_current_recent else Styles.HIGHLIGHTED_FRAME
        )
        for child in current_frame.winfo_children():
            if isinstance(child, ttk.Label):
                if child.cget("font") == Fonts.SMALL:
                    child.configure(
                        style=Styles.HIGHLIGHTED_RECENT_URL_LABEL
                        if is_current_recent
                        else Styles.HIGHLIGHTED_URL_LABEL
                    )
                else:
                    child.configure(
                        style=Styles.HIGHLIGHTED_RECENT_LABEL
                        if is_current_recent
                        else Styles.HIGHLIGHTED_LABEL
                    )

        # Scroll to keep entry visible
        self._scroll_to_entry(index)

        # Return the entry object
        return current_details["entry"]

    def _scroll_to_entry(self, index: int):
        """Auto-scroll canvas to keep the entry at given index visible"""
        if not self.canvas or not self.entry_frames or index < 0 or index >= len(self.entry_frames):
            return

        # Need to update canvas first to get accurate positions
        self.canvas.update_idletasks()

        entry_frame = self.entry_frames[index]["frame"]

        # Get entry's position and height
        frame_y = entry_frame.winfo_y()
        frame_height = entry_frame.winfo_height()

        # Get scroll region
        scroll_region = self.canvas.bbox("all")
        if not scroll_region:
            return

        total_height = scroll_region[3]
        if total_height == 0:
            return

        # Get canvas visible height
        canvas_height = self.canvas.winfo_height()
        if canvas_height == 0:
            return

        # Get current scroll position
        scroll_top = self.canvas.yview()[0] * total_height
        scroll_bottom = scroll_top + canvas_height

        # Scroll up if entry is above visible area
        if frame_y < scroll_top:
            self.canvas.yview_moveto(frame_y / total_height)
        # Scroll down if entry is below visible area
        elif frame_y + frame_height > scroll_bottom:
            new_top = (frame_y + frame_height - canvas_height) / total_height
            self.canvas.yview_moveto(max(0, new_top))

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if not self.canvas:
            return
        # Windows scroll direction
        if event.delta < 0:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(-3, "units")

    def _on_entry_click(self, entry):
        """Handle click on an entry - select it"""
        from .events import EventBus, Events

        EventBus.publish(Events.SELECT, entry)

    def get_current_highlight(self) -> int:
        """Get the index of the currently highlighted entry"""
        return self.current_highlight

    def get_current_highlighted_entry_details(self) -> Optional[Dict[str, Any]]:
        """Get the details of the currently highlighted entry"""
        if 0 <= self.current_highlight < len(self.entry_frames):
            return self.entry_frames[self.current_highlight]
        return None

    def get_entry_count(self) -> int:
        """Get the number of entries"""
        return len(self.entry_frames)
