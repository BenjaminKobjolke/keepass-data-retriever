from typing import Any, Callable, Dict, List
from .state_manager import StateManager, AppState
from .logger import Logger

# Get logger instance
logger = Logger.get_instance()


class StateHandler:
    """Handles application state transitions and state-specific logic"""

    def __init__(
        self,
        state_manager: StateManager,
        on_search: Callable,
        on_get_recent_entries: Callable,
        show_entries_callback: Callable,
        show_selected_entry_callback: Callable,
        reset_callback: Callable,
        set_search_text_callback: Callable,
        show_search_callback: Callable,
    ):
        """Initialize the state handler"""
        self.state_manager = state_manager
        self.on_search = on_search
        self.on_get_recent_entries = on_get_recent_entries
        self.show_entries_callback = show_entries_callback
        self.show_selected_entry_callback = show_selected_entry_callback
        self.reset_callback = reset_callback
        self.set_search_text_callback = set_search_text_callback
        self.show_search_callback = show_search_callback
        self._restoring_state = False

    def handle_state_change(self, state: AppState, data: Dict[str, Any]) -> None:
        """Handle state changes"""
        logger.debug(f"Handling state change to {state}")

        if state == AppState.INITIAL:
            self._handle_initial_state(data)
        elif state == AppState.SEARCH:
            self._handle_search_state(data)
        elif state == AppState.RESULTS_LIST:
            self._handle_results_list_state(data)
        elif state == AppState.ENTRY_ACTIONS:
            self._handle_entry_actions_state(data)
        elif state == AppState.LOCKED:
            self._handle_locked_state(data)

    def _handle_initial_state(self, data: Dict[str, Any]) -> None:
        """Handle INITIAL state"""
        logger.debug("Handling INITIAL state")
        self.reset_callback()

        # Check for recent entries
        try:
            # Get window relations manager from data
            window_relations_manager = data.get("window_relations_manager")
            logger.debug(f"Window relations manager from data: {window_relations_manager}")

            if window_relations_manager:
                # Get current window title
                current_window_title = window_relations_manager.current_window_title
                logger.debug(f"Current window title: {current_window_title}")

                # Get recent entry IDs for current window
                recent_entry_ids = window_relations_manager.get_recent_entries_for_current_window()
                logger.debug(f"Recent entry IDs for current window: {recent_entry_ids}")

                if recent_entry_ids:
                    # Get entries from KeePass database
                    logger.debug(
                        f"Getting entries from KeePass database for IDs: {recent_entry_ids}"
                    )
                    try:
                        recent_entries = self.on_get_recent_entries(recent_entry_ids)

                        if recent_entries:
                            logger.debug(f"Found {len(recent_entries)} recent entries")
                            # Log entry titles for debugging
                            for i, entry in enumerate(recent_entries):
                                logger.debug(f"  Entry {i + 1}: {entry.title} (UUID: {entry.uuid})")

                            # Show recent entries
                            self.show_recent_entries(recent_entries)
                            return
                        else:
                            logger.debug("No entries returned from on_get_recent_entries")
                            logger.debug(f"Entry IDs that were searched for: {recent_entry_ids}")
                    except Exception as db_error:
                        logger.error(f"Error retrieving entries from database: {db_error}")
                        logger.debug("Falling back to showing search input")
                else:
                    logger.debug("No recent entry IDs found for current window")
            else:
                logger.debug("No window relations manager in data")
        except Exception as e:
            logger.error(f"Error getting recent entries: {e}")
            import traceback

            logger.error(traceback.format_exc())

        # No recent entries or error occurred, just show search
        logger.debug("No recent entries to show or error occurred, showing search input")

        # Make sure we don't show entries from previous windows
        # This is handled in SearchWindow._handle_reset, but we'll also do it here for safety
        self.reset_callback()

        # Show search input
        self.show_search_callback()

        # Clear the search input
        self.set_search_text_callback("")

    def _handle_search_state(self, data: Dict[str, Any]) -> None:
        """Handle SEARCH state"""
        logger.debug("Handling SEARCH state")
        search_term = data.get("search_term", "")

        if search_term:
            # Perform search with the term
            self.set_search_text_callback(search_term)
            self.on_search(search_term)
        else:
            # Just show search input
            self.show_search_callback()

    def _handle_results_list_state(self, data: Dict[str, Any]) -> None:
        """Handle RESULTS_LIST state"""
        logger.debug("Handling RESULTS_LIST state")
        entries = data.get("entries", [])
        if entries:
            # Use skip_state_transition=True to avoid infinite loop
            self.show_entries_callback(entries, keep_search_mode=True, skip_state_transition=True)

    def _handle_entry_actions_state(self, data: Dict[str, Any]) -> None:
        """Handle ENTRY_ACTIONS state"""
        logger.debug("Handling ENTRY_ACTIONS state")
        entry = data.get("entry")
        if entry:
            # Use skip_state_transition=True to avoid duplicate action buttons
            self.show_selected_entry_callback(entry, skip_state_transition=True)

    def _handle_locked_state(self, data: Dict[str, Any]) -> None:
        """Handle LOCKED state"""
        logger.debug("Handling LOCKED state")
        # This would typically trigger the password dialog
        pass

    def show_recent_entries(self, entries: List[Any]) -> None:
        """Show recent entries for the current window"""
        if not entries:
            return

        logger.debug(f"Showing {len(entries)} recent entries")

        # Transition to RESULTS_LIST state
        self.state_manager.transition_to(AppState.RESULTS_LIST, {"entries": entries})

        # Show entries in the results view and keep search input active
        # Skip state transition to avoid infinite loop
        self.show_entries_callback(
            entries, keep_search_mode=True, skip_state_transition=True, is_recent_list=True
        )

    def restore_previous_state(self) -> bool:
        """Restore previous state based on what was active before hiding"""
        previous_state = self.state_manager.get_previous_state()
        previous_data = self.state_manager.get_previous_state_data()

        if not previous_state:
            logger.debug("No previous state to restore")
            return False

        logger.debug(f"Restoring previous state: {previous_state}")

        # Set a flag to indicate we're restoring state
        self._restoring_state = True

        try:
            if previous_state == AppState.RESULTS_LIST and "entries" in previous_data:
                # Restore the results list with the entries
                logger.debug(f"Restoring results list with {len(previous_data['entries'])} entries")
                # Determine if this was a recent list. If data has 'is_recent_list_active' or similar, use it.
                # For now, assume if it was RESULTS_LIST, it could be search or recent.
                # If `previous_data` had an indicator for `is_recent_list`, we'd use it.
                # Let's assume for now it was a search result unless specific logic for recent is added here.
                self.show_entries_callback(
                    previous_data["entries"],
                    keep_search_mode=True,
                    skip_state_transition=True,
                    is_recent_list=False,
                )  # Default to False for generic restore
                # Set the current state directly without triggering listeners
                self.state_manager._current_state = AppState.RESULTS_LIST
                self.state_manager._state_data = previous_data
                return True
            elif previous_state == AppState.ENTRY_ACTIONS and "entry" in previous_data:
                # Restore the entry actions with the selected entry
                logger.debug(f"Restoring entry actions for entry: {previous_data['entry'].title}")
                self.show_selected_entry_callback(
                    previous_data["entry"], skip_state_transition=True
                )
                # Set the current state directly without triggering listeners
                self.state_manager._current_state = AppState.ENTRY_ACTIONS
                self.state_manager._state_data = previous_data
                return True
            else:
                logger.debug("No specific state to restore")
                return False
        finally:
            self._restoring_state = False
