"""Results display controller for search results."""

from typing import List, Any
from .state_manager import StateManager, AppState
from .logger import Logger

logger = Logger.get_instance()


class ResultsDisplay:
    """Controls how search results are displayed."""

    def __init__(self, results_view, window_manager, status_display,
                 input_manager, entry_actions_handler, state_manager: StateManager,
                 recent_entries_handler):
        self.results_view = results_view
        self.window_manager = window_manager
        self.status_display = status_display
        self.input_manager = input_manager
        self.entry_actions_handler = entry_actions_handler
        self.state_manager = state_manager
        self.recent_entries_handler = recent_entries_handler

    def show_entries(self, entries: List[Any], keep_search_mode: bool = True,
                     skip_state_transition: bool = False, is_recent_list: bool = False):
        """
        Display entries with appropriate mode.

        Args:
            entries: List of entries to display
            keep_search_mode: Keep search input active
            skip_state_transition: Skip state manager transition
            is_recent_list: True if showing recent entries (deletable)
        """
        logger.debug(f"Showing {len(entries)} entries, keep_search_mode={keep_search_mode}, "
                    f"is_recent_list={is_recent_list}")

        # Update recent list tracking
        self.recent_entries_handler.set_recent_list_active(is_recent_list)

        # Clear previous results
        self.results_view.clear()
        self.entry_actions_handler.cleanup()

        if not entries:
            self.window_manager.set_expanded(False)
            self.status_display.set_text("No entries found")
            return

        if len(entries) == 1 and not keep_search_mode:
            self._show_single_entry(entries[0], skip_state_transition)
        else:
            self._show_multiple_entries(entries, keep_search_mode, skip_state_transition,
                                        is_recent_list)

    def _show_single_entry(self, entry: Any, skip_state_transition: bool):
        """Show single entry with actions directly."""
        # Transition to ENTRY_ACTIONS state
        if not skip_state_transition:
            self.state_manager.transition_to(AppState.ENTRY_ACTIONS, {'entry': entry})

        self.window_manager.set_expanded(True)
        self.status_display.show_search_results([entry], entry)

        # Set the entry in InputManager before showing actions
        logger.debug("Single entry, showing actions")
        self.input_manager.show_list([entry])

        # Show the selected entry with action buttons
        self.entry_actions_handler.show_selected_entry(entry)

        self.window_manager.auto_resize()

    def _show_multiple_entries(self, entries: List[Any], keep_search_mode: bool,
                               skip_state_transition: bool, is_recent_list: bool):
        """Show multiple entries in list view."""
        # Transition to RESULTS_LIST state
        if not skip_state_transition:
            self.state_manager.transition_to(AppState.RESULTS_LIST, {'entries': entries})

        self.window_manager.set_expanded(True)
        self.results_view.show_entries(entries, is_recent_list=is_recent_list)
        self.status_display.show_search_results(entries)

        if keep_search_mode:
            # Store entries but keep search input active
            logger.debug("Keeping search input active")
            self.input_manager.set_entries(entries)
            self.results_view.current_highlight = -1
            self.input_manager.show_search()
        else:
            # Show list mode
            logger.debug("Showing list mode")
            self.input_manager.show_list(entries)

            # Highlight the first entry by default
            if entries:
                entry = self.results_view.highlight_entry(0)
                if entry:
                    self.input_manager.current_entry = entry

        self.window_manager.auto_resize()

    def show_selected_entry(self, entry: Any, skip_state_transition: bool = False):
        """
        Display single selected entry with actions.

        Args:
            entry: The entry to display
            skip_state_transition: Skip state manager transition
        """
        logger.debug(f"Showing selected entry: {entry.title}")
        self.results_view.clear()
        self.status_display.show_selected_entry(entry)

        # Ensure InputManager has the current entry before showing actions
        self.input_manager.current_entry = entry
        self.input_manager.show_actions()

        # Show the selected entry with action buttons
        self.entry_actions_handler.show_selected_entry(entry)

        self.window_manager.set_expanded(True)
        self.window_manager.auto_resize()
