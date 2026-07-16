"""Entry search and lookup service for KeePass database."""

import uuid
from ui.logger import Logger


class EntrySearchService:
    """Handles searching and finding entries in the KeePass database."""

    def __init__(self, database_manager):
        """
        Initialize search service.

        Args:
            database_manager: DatabaseManager instance for database access
        """
        self.database_manager = database_manager
        self.logger = Logger.get_instance()

    def search_entries(self, search_term):
        """
        Search for entries matching the search term.

        Args:
            search_term: Search string to match against entry titles and usernames

        Returns:
            list: List of matching KeePass entries
        """
        if self.database_manager.is_locked or not self.database_manager.kp:
            return []

        entries = []
        # Split search term into individual words
        search_terms = search_term.lower().split()

        for entry in self.database_manager.kp.entries:
            title = (entry.title or "").lower()
            username = (entry.username or "").lower()

            # Replace hyphens with spaces to improve matching
            searchable_title = title.replace("-", " ")
            searchable_username = username.replace("-", " ")

            # Check if all search terms are found in either title or username
            if all(
                term in searchable_title or term in searchable_username for term in search_terms
            ):
                entries.append(entry)

        return entries

    def find_entries_by_uuids(self, uuids):
        """
        Find entries by their UUIDs.

        Args:
            uuids: List of UUID strings

        Returns:
            list: List of found KeePass entries
        """
        self.logger.debug(f"Searching for {len(uuids)} UUIDs in KeePass database: {uuids}")

        # Ensure database is connected before attempting to find entries
        if not self.database_manager.lazy_connect_database():
            self.logger.debug("Cannot find entries: database connection failed")
            return []

        if self.database_manager.is_locked or not self.database_manager.kp:
            self.logger.debug("Cannot find entries: database is locked or not connected")
            return []

        self.logger.debug(f"Finding entries for {len(uuids)} UUIDs: {uuids}")

        # Check if we have any entries at all
        if not self.database_manager.kp.entries:
            self.logger.debug("No entries in the database")
            return []

        # Log total number of entries in database for debugging
        self.logger.debug(f"Total entries in database: {len(self.database_manager.kp.entries)}")

        entries = []
        for uuid_str in uuids:
            try:
                # Convert string UUID to UUID object
                uuid_obj = uuid.UUID(uuid_str)
                self.logger.debug(f"Looking up entry with UUID: {uuid_str}")

                # Use PyKeePass's find_entries method with the uuid parameter
                entry = self.database_manager.kp.find_entries(uuid=uuid_obj, first=True)
                if entry:
                    self.logger.debug(f"Found entry: {entry.title} (UUID: {entry.uuid})")
                    entries.append(entry)
                else:
                    self.logger.debug(
                        f"No entry found for UUID: {uuid_str}, trying manual search..."
                    )

                    # Try to find the entry by iterating through all entries
                    # This is a fallback in case the find_entries method doesn't work
                    found = False
                    for e in self.database_manager.kp.entries:
                        if str(e.uuid) == uuid_str:
                            self.logger.debug(
                                f"Found entry by manual search: {e.title} (UUID: {e.uuid})"
                            )
                            entries.append(e)
                            found = True
                            break

                    if not found:
                        self.logger.debug(f"Entry not found even with manual search: {uuid_str}")
            except Exception as e:
                self.logger.error(f"Error finding entry with UUID {uuid_str}: {e}")
                import traceback

                self.logger.error(traceback.format_exc())

        self.logger.debug(f"Found {len(entries)} entries total")
        return entries

    def get_recent_entries(self, entry_ids):
        """
        Get entries by their UUIDs.

        Args:
            entry_ids: List of entry UUID strings

        Returns:
            list: List of found KeePass entries
        """
        self.logger.debug(f"Getting recent entries for IDs: {entry_ids}")

        if self.database_manager.is_locked:
            self.logger.debug("Database is locked, cannot get entries")
            return []

        if not self.database_manager.kp:
            self.logger.debug("No database connection, cannot get entries")
            return []

        entries = self.find_entries_by_uuids(entry_ids)
        self.logger.debug(f"Found {len(entries)} entries")

        # Log entry titles for debugging
        for entry in entries:
            self.logger.debug(f"Found entry: {entry.title}")

        return entries
