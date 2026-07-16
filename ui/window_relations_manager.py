import json
import os
import win32gui
import time
from typing import List, Optional, Any
from .logger import Logger

# Get logger instance
logger = Logger.get_instance()


class WindowRelationsManager:
    def __init__(self, file_path: str = "window-relations.json"):
        self.file_path = file_path
        self.relations = self._load_relations()
        self.current_window_title = None

    def _load_relations(self) -> List:
        """Load existing relations from JSON file or create new structure"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    relations = json.load(f)
                    logger.debug(f"Loaded {len(relations)} window relations from {self.file_path}")
                    return relations
            except Exception as e:
                logger.error(f"Error loading window relations: {e}")
                return []
        logger.debug(f"Window relations file {self.file_path} not found, creating new")
        return []  # Return empty array instead of empty dict

    def _save_relations(self) -> None:
        """Save relations to JSON file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.relations, f, indent=2)
                logger.debug(f"Saved {len(self.relations)} window relations to {self.file_path}")
        except Exception as e:
            logger.error(f"Error saving window relations: {e}")

    def _find_window_index(self, window_title: str) -> int:
        """Find the index of a window in the relations array"""
        for i, window_data in enumerate(self.relations):
            if window_data.get("title") == window_title:
                return i
        return -1

    def log_active_window(self) -> Optional[str]:
        """Log the currently active window title"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)

            if window_title:
                logger.debug(f"Active window title: {window_title}")
                logger.debug(f"DEBUG: Current window title detected: '{window_title}'")
                self.current_window_title = window_title

                # Find window in relations
                window_index = self._find_window_index(window_title)
                logger.debug(f"Window index in relations: {window_index}")

                if window_index == -1:
                    # Window not found, add it
                    logger.debug(f"Adding new window title to relations: {window_title}")
                    self.relations.append(
                        {
                            "title": window_title,
                            "count": 1,
                            "last_accessed": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "recent_entries": [],  # List to store the last 3 entry IDs
                        }
                    )
                else:
                    # Window found, update it
                    logger.debug(f"Updating existing window title in relations: {window_title}")
                    self.relations[window_index]["count"] += 1
                    self.relations[window_index]["last_accessed"] = time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                # Save to file
                self._save_relations()
                return window_title

            logger.debug("No active window title found")
            return None
        except Exception as e:
            logger.error(f"Error logging active window: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def log_entry_selection(self, entry: Any) -> None:
        """Log the selected KeePass entry for the current window"""
        if not self.current_window_title or not entry:
            logger.debug(
                f"Cannot log entry selection: window_title={self.current_window_title}, entry={entry}"
            )
            return

        try:
            # Get entry ID - assuming entry has an 'uuid' attribute
            # If not, we'll need to use another unique identifier
            entry_id = str(entry.uuid) if hasattr(entry, "uuid") else str(id(entry))
            logger.debug(
                f"Logging entry selection: entry_id={entry_id}, window_title={self.current_window_title}"
            )

            # Find window in relations
            window_index = self._find_window_index(self.current_window_title)
            logger.debug(f"Window index in relations: {window_index}")

            if window_index == -1:
                logger.debug(f"Window title not found in relations: {self.current_window_title}")
                return

            # Get the window data
            window_data = self.relations[window_index]

            # Get the recent entries list
            recent_entries = window_data.get("recent_entries", [])
            logger.debug(f"Current recent entries: {recent_entries}")

            # Remove this entry if it already exists in the list
            if entry_id in recent_entries:
                logger.debug(f"Entry already in recent list, removing: {entry_id}")
                recent_entries.remove(entry_id)

            # Add the entry to the beginning of the list
            recent_entries.insert(0, entry_id)
            logger.debug(f"Added entry to beginning of list: {entry_id}")

            # Keep only the last 3 entries
            window_data["recent_entries"] = recent_entries[:3]
            logger.debug(f"Updated recent entries (max 3): {window_data['recent_entries']}")

            # Save to file
            self._save_relations()
        except Exception as e:
            logger.error(f"Error logging entry selection: {e}")
            import traceback

            logger.error(traceback.format_exc())

    def get_recent_entries_for_current_window(self) -> List[str]:
        """Get recent entry IDs for the current window"""
        if not self.current_window_title:
            logger.debug("No current window title, cannot get recent entries")
            logger.debug("DEBUG: No current window title, cannot get recent entries")
            return []

        logger.debug(f"Getting recent entries for window: {self.current_window_title}")
        logger.debug(f"DEBUG: Looking for recent entries for window: '{self.current_window_title}'")
        window_index = self._find_window_index(self.current_window_title)
        logger.debug(f"Window index in relations: {window_index}")

        if window_index == -1:
            logger.debug(f"Window title not found in relations: {self.current_window_title}")
            logger.debug(
                f"DEBUG: Window title '{self.current_window_title}' not found in window-relations.json"
            )
            return []

        recent_entries = self.relations[window_index].get("recent_entries", [])
        logger.debug(f"Found recent entries: {recent_entries}")
        logger.debug(
            f"DEBUG: Found {len(recent_entries)} recent entries for this window: {recent_entries}"
        )
        return recent_entries

    def remove_recent_entry(self, window_title: str, entry_uuid: str) -> None:
        """Remove a specific entry_uuid from the recent_entries list for the given window_title."""
        if not window_title:
            logger.warning("Cannot remove recent entry: window_title is None or empty.")
            return

        window_index = self._find_window_index(window_title)
        if window_index == -1:
            logger.warning(
                f"Cannot remove recent entry: window title '{window_title}' not found in relations."
            )
            return

        window_data = self.relations[window_index]
        recent_entries = window_data.get("recent_entries", [])

        if entry_uuid in recent_entries:
            recent_entries.remove(entry_uuid)
            # No need to reassign `window_data["recent_entries"] = recent_entries` as `recent_entries` is a reference to the list in `window_data`
            self._save_relations()
            logger.info(
                f"Removed entry UUID '{entry_uuid}' from recent entries for window '{window_title}'."
            )
        else:
            logger.debug(
                f"Entry UUID '{entry_uuid}' not found in recent_entries for window '{window_title}'. No action taken."
            )
