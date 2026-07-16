"""Recent entries management handler."""

from typing import Any
from .state_manager import StateManager, AppState
from .logger import Logger

logger = Logger.get_instance()


class RecentEntriesHandler:
    """Manages recent entries display and deletion."""

    def __init__(self, window_relations_manager, state_manager: StateManager):
        self.window_relations_manager = window_relations_manager
        self.state_manager = state_manager
        self.is_recent_list_active: bool = False

    def set_recent_list_active(self, is_active: bool):
        """
        Track whether current list is recent entries.

        Args:
            is_active: True if current list shows recent entries
        """
        self.is_recent_list_active = is_active

    def handle_delete_recent_entry(self, entry_to_delete: Any):
        """
        Delete a recent entry and refresh view.

        Args:
            entry_to_delete: The entry to delete from recent entries
        """
        if not self.is_recent_list_active:
            logger.debug("Delete key pressed, but not in recent list mode. Ignoring.")
            return

        if not entry_to_delete:
            logger.warning("Delete recent entry requested, but no entry is selected.")
            return

        current_window_title = self.window_relations_manager.current_window_title
        if not current_window_title:
            logger.warning("Delete recent entry requested, but current window title is unknown.")
            return

        try:
            entry_uuid = str(entry_to_delete.uuid)
            logger.info(
                f"Requesting deletion of recent entry UUID '{entry_uuid}' "
                f"for window '{current_window_title}'."
            )
            self.window_relations_manager.remove_recent_entry(current_window_title, entry_uuid)

            # Refresh the view by transitioning to INITIAL state
            logger.debug("Transitioning to INITIAL state to refresh recent entries view.")
            self.state_manager.transition_to(
                AppState.INITIAL, {"window_relations_manager": self.window_relations_manager}
            )
        except AttributeError:
            logger.error(f"Failed to get UUID from entry: {entry_to_delete}. Cannot delete.")
        except Exception as e:
            logger.error(f"Error during recent entry deletion: {e}")
