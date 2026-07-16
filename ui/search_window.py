"""Main search window for KeePass Data Retriever application."""

import tkinter as tk
from typing import Callable, List, Any, Dict
import sys
import os

from .window_manager import WindowManager
from .input import InputManager, InputMode
from .status_display import StatusDisplay
from .results_view import ResultsView
from .hotkey_manager import HotkeyManager
from .dark_entry import DarkEntry
from .window_relations_manager import WindowRelationsManager
from .state_manager import StateManager, AppState
from .keyboard_handler import KeyboardHandler
from .entry_actions_handler import EntryActionsHandler
from .state_handler import StateHandler
from .logger import Logger
from .settings_window import SettingsWindow
from .theme_manager import ThemeManager
from .events import EventBus, Events

# Import new handlers
from .window_lifecycle import WindowLifecycle
from .highlight_handler import HighlightHandler
from .recent_entries_handler import RecentEntriesHandler
from .results_display import ResultsDisplay

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config

# Get logger instance
logger = Logger.get_instance()


class SearchWindow:
    """Main window coordinator for KeePass Data Retriever application."""

    def __init__(
        self,
        on_search: Callable,
        on_action: Callable,
        on_select: Callable,
        on_connect: Callable,
        on_get_recent_entries: Callable,
    ):
        """Initialize the search window."""
        # Initialize state manager
        self.state_manager = StateManager()

        # Create root window
        self.root = tk.Tk()

        # Initialize window relations manager
        self.window_relations_manager = WindowRelationsManager()

        # Initialize components
        self.window = WindowManager(self.root)
        self.status = StatusDisplay(self.window.get_main_frame())

        # Store callbacks
        self.on_search = on_search
        self.on_action = on_action
        self.on_select = on_select
        self.on_connect = on_connect
        self.on_get_recent_entries = on_get_recent_entries

        # Initialize keyboard handler
        self.keyboard_handler = KeyboardHandler()

        # Initialize entry actions handler
        self.entry_actions_handler = EntryActionsHandler(
            self.root,
            self.window.get_main_frame(),
            self.state_manager,
            self.on_action,
            self.window_relations_manager,
            self._do_hide,
        )

        # Initialize recent entries handler
        self.recent_entries_handler = RecentEntriesHandler(
            self.window_relations_manager, self.state_manager
        )

        # Initialize input manager
        self.input = InputManager(self.window.get_main_frame(), DarkEntry, self.state_manager)

        # Subscribe to EventBus events
        EventBus.subscribe(Events.SEARCH, self._handle_search)
        EventBus.subscribe(Events.SELECT, self._handle_select)
        EventBus.subscribe(Events.ACTION, self._handle_action_event)
        EventBus.subscribe(Events.HIDE, self._do_hide)
        EventBus.subscribe(Events.RESET, self._handle_reset)
        EventBus.subscribe(Events.HIGHLIGHT_CHANGE, self._handle_highlight_change)
        EventBus.subscribe(Events.ACTION_HIGHLIGHT_CHANGE, self._handle_action_highlight_event)
        EventBus.subscribe(Events.DELETE_ENTRY, self._handle_delete_recent_entry)
        EventBus.subscribe(Events.SHOW_INITIAL, self.show_initial_view)
        EventBus.subscribe(Events.EXIT, self._handle_exit)
        EventBus.subscribe(Events.RELOAD, self._handle_reload)
        EventBus.subscribe(Events.SETTINGS, self._handle_settings)
        EventBus.subscribe(Events.FRAME, self._handle_frame)
        EventBus.subscribe(Events.FILTER, self._handle_filter)

        # Settings window reference
        self.settings_window = None

        # Initialize results view
        self.results = ResultsView(self.window.get_main_frame(), self.state_manager)

        # Initialize state handler
        self.state_handler = StateHandler(
            self.state_manager,
            self.on_search,
            self.on_get_recent_entries,
            self.show_entries,
            self.show_selected_entry,
            self._handle_reset,
            self.input.set_search_text,
            self.input.show_search,
        )

        # Initialize highlight handler
        self.highlight_handler = HighlightHandler(self.results, self.input, self.window)

        # Initialize results display controller
        self.results_display = ResultsDisplay(
            self.results,
            self.window,
            self.status,
            self.input,
            self.entry_actions_handler,
            self.state_manager,
            self.recent_entries_handler,
        )

        # Initialize window lifecycle controller
        self.lifecycle = WindowLifecycle(
            self.window,
            self.state_manager,
            self.window_relations_manager,
            self.state_handler,
            self.on_connect,
            self.input,
        )

        # Bind events
        self.root.bind("<Return>", self._handle_return)
        self.root.bind("<Escape>", lambda e: self.hide())
        self.root.bind("<FocusOut>", self.window.check_focus)

        # Start hotkey listener
        self.hotkey = HotkeyManager(self.show_window, root=self.root)

        # Register as state listener
        self.state_manager.register_listener(self)

    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes."""
        logger.debug(f"SearchWindow: State changed to {state}")

        # Add window_relations_manager to data for state handler
        if "window_relations_manager" not in data:
            data["window_relations_manager"] = self.window_relations_manager

        # Let the state handler handle the state change
        if state != AppState.HIDDEN:
            self.state_handler.handle_state_change(state, data)
        elif state == AppState.HIDDEN:
            self._do_hide()

    def _handle_search(self, search_term: str):
        """Handle search request."""
        logger.debug(f"Search request with term: '{search_term}'")
        self.state_manager.transition_to(AppState.SEARCH, {"search_term": search_term})
        self.on_search(search_term)

    def _handle_select(self, entry: Any):
        """Handle entry selection."""
        logger.debug(f"Entry selected: {entry.title}")
        self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {"entry": entry})
        self.on_select(entry)

    def _handle_reset(self):
        """Handle reset request."""
        logger.debug("Reset request")

        # Clear results and actions
        self.results.clear()
        self.entry_actions_handler.cleanup()

        # Check if we're in INITIAL state
        current_state = self.state_manager.get_current_state()
        if current_state == AppState.INITIAL:
            logger.debug("In INITIAL state, clearing entries from previous windows")
            self.input.clear_entries()
            self.recent_entries_handler.set_recent_list_active(False)
            self.window.set_expanded(False)
            self.status.set_text("")
            return

        # Check if we have entries to show
        if self.input.entries and len(self.input.entries) > 0:
            logger.debug(f"Showing {len(self.input.entries)} entries")
            self.show_entries(
                self.input.entries,
                keep_search_mode=True,
                skip_state_transition=True,
                is_recent_list=False,
            )
            self.window.set_expanded(True)
            self.status.set_text("Recent entries for this window:")
            self.results.frame.pack(fill=tk.BOTH, expand=True)
            self.window.auto_resize()
        else:
            logger.debug("No entries to show")
            self.window.set_expanded(False)
            self.status.set_text("")

    def _handle_return(self, event):
        """Handle Return key."""
        if self.input.current_mode == InputMode.ACTION and self.input.current_entry:
            if self.entry_actions_handler.handle_action_return(self.input.current_entry):
                return "break"
        return self.input.handle_return()

    def show_window(self):
        """Show the window."""
        if self.lifecycle.show():
            # Schedule focus after short delay
            self.root.after(100, self.lifecycle.ensure_focus)

    def show_recent_entries(self, entries):
        """Show recent entries for the current window."""
        self.state_handler.show_recent_entries(entries)

    def show_initial_view(self):
        """Show the initial view with recent entries for the current window."""
        self.state_manager.transition_to(AppState.INITIAL)

    def hide(self):
        """Hide the window."""
        self.lifecycle.hide()

    def _do_hide(self):
        """Internal hide implementation."""
        self.lifecycle.hide()

    def _handle_highlight_change(self, direction: str):
        """Handle highlight change in results view."""
        self.highlight_handler.handle_highlight_change(direction)

    def _handle_action_event(self, data: Dict[str, Any]):
        """Handle action event from EventBus."""
        action_id = data.get("action_id")
        entry = data.get("entry")
        if action_id and entry:
            self.entry_actions_handler.handle_action(action_id, entry)

    def _handle_action_highlight_event(self, direction: str):
        """Handle action highlight change event from EventBus."""
        self.entry_actions_handler.handle_highlight_change(direction)

    def _handle_delete_recent_entry(self, entry_to_delete: Any):
        """Handle delete request for a recent entry."""
        self.recent_entries_handler.handle_delete_recent_entry(entry_to_delete)

    def _handle_filter(self, filtered_entries: List[Any]):
        """Handle filter event - update results display with filtered entries."""
        logger.debug(f"Filter event received with {len(filtered_entries)} entries")
        # Update only the results view, don't change state
        self.results.clear()
        if filtered_entries:
            # Determine if this is a recent list based on the handler state
            is_recent = self.recent_entries_handler.is_recent_list_active
            self.results.show_entries(filtered_entries, is_recent_list=is_recent)
            self.status.show_search_results(filtered_entries)
            # Window collapses on every show(); expand or auto_resize is a no-op
            self.window.set_expanded(True)
            self.window.auto_resize()
        else:
            self.status.set_text("No matching entries")

    def show_entries(
        self,
        entries: List[Any],
        keep_search_mode=True,
        skip_state_transition=False,
        is_recent_list: bool = False,
    ):
        """Show search results."""
        self.results_display.show_entries(
            entries, keep_search_mode, skip_state_transition, is_recent_list
        )

    def show_selected_entry(self, entry: Any, skip_state_transition=False):
        """Show selected entry."""
        self.results_display.show_selected_entry(entry, skip_state_transition)

    def set_search_text(self, text: str):
        """Set the search input text."""
        self.input.set_search_text(text)

    def set_status(self, text: str):
        """Set status text."""
        self.status.set_text(text)

    def _handle_exit(self):
        """Handle exit command."""
        logger.info("Exit command detected, closing application")
        if self.root:
            self.root.quit()

    def _handle_reload(self):
        """Handle reload command."""
        logger.info("Reload command detected")
        if hasattr(self, "reload_handler") and self.reload_handler:
            self.reload_handler()
        else:
            logger.warning("No reload handler configured")

    def _handle_settings(self):
        """Handle settings command."""
        logger.info("Settings command detected, opening settings window")
        if self.settings_window is None:
            self.settings_window = SettingsWindow(
                on_close=self._on_settings_closed, on_apply=self._on_settings_applied
            )

    def _handle_frame(self):
        """Handle frame command: toggle native window frames for all windows."""
        show_frame = not config.get_show_frame()
        logger.info(f"Frame command detected, show_frame -> {show_frame}")
        config.set_show_frame(show_frame)
        config.save_config()
        self.window.refresh_frame()

    def _on_settings_closed(self):
        """Called when settings window is closed."""
        self.settings_window = None

    def _on_settings_applied(self):
        """Called when settings are applied."""
        logger.info("Settings applied, reloading theme")

        # Reload theme colors in ThemeManager
        ThemeManager.reload_colors()

        # Reconfigure TTK styles
        ThemeManager.configure_styles(self.window.style)

        # Update input widgets
        self.input.search_input.update_theme()
        self.input.list_input.update_theme()
        self.input.action_input.update_theme()

        # Reconfigure results view highlight styles
        self.results._configure_highlight_styles()

        # Re-apply frame preference (no-op unless show_frame changed in settings)
        self.window.refresh_frame()

        # Update window/frame backgrounds
        self.window.get_main_frame().configure(style="Dark.TFrame")

        logger.info("Theme update complete")

    def run(self):
        """Start the application."""
        hotkey = config.get_search_hotkey()
        logger.info(f"KeePass Search running. Press {hotkey} to open search window.")
        logger.info("Right-click the window for menu options.")
        logger.info("Type /exit in any search box to exit the application.")
        logger.info("Type /reload in any search box to reload the database.")
        logger.info("Type /settings in any search box to open settings.")
        self.root.mainloop()
