#!/usr/bin/env python3

import atexit
import sys
import pyperclip
import win32api
import win32event
import winerror
from tkinter import messagebox
from ui.search_window import SearchWindow
from config import config
from database.database_manager import DatabaseManager
from database.database_lock_manager import DatabaseLockManager
from services.entry_search_service import EntrySearchService
from ui.logger import Logger

logger = Logger.get_instance()


class KeePassRetriever:
    def __init__(self):
        # Single instance check - must be first
        self.mutex = None
        self._mutex_released = False
        if not self._ensure_single_instance():
            messagebox.showerror("Already Running", "KeePass Data Retriever is already running.")
            sys.exit(0)

        # Safety net: release mutex on interpreter shutdown / uncaught exception
        atexit.register(self._release_mutex)

        # Initialize managers
        self.db_manager = DatabaseManager()
        self.lock_manager = DatabaseLockManager(self.db_manager)
        self.search_service = EntrySearchService(self.db_manager)

        self.window = None

    def _ensure_single_instance(self):
        """Ensure only one instance of the application is running using a named mutex."""
        mutex_name = "Global\\KeePassDataRetrieverMutex"
        self.mutex = win32event.CreateMutex(None, False, mutex_name)
        last_error = win32api.GetLastError()

        if last_error == winerror.ERROR_ALREADY_EXISTS:
            return False
        return True

    def _release_mutex(self):
        """Release the single-instance mutex. Idempotent."""
        if self._mutex_released:
            return
        if self.mutex:
            try:
                win32api.CloseHandle(self.mutex)
            except Exception:
                pass
        self._mutex_released = True

    def handle_search(self, search_term):
        """Handle search request."""
        if self.db_manager.is_locked:
            return

        entries = self.search_service.search_entries(search_term)
        self.window.show_entries(entries, is_recent_list=False)

    def handle_select(self, entry):
        """Handle entry selection."""
        if self.db_manager.is_locked:
            return
        self.window.show_selected_entry(entry)

    def handle_action(self, action, entry=None):
        """Handle action request."""
        if self.db_manager.is_locked:
            return

        if not entry:
            entry = self.window.input.single_entry
        if not entry:
            logger.debug("No entry selected")
            return

        try:
            if action == "username" and entry.username:
                pyperclip.copy(entry.username)
            elif action == "password" and entry.password:
                pyperclip.copy(entry.password)
            elif action == "url" and entry.url:
                pyperclip.copy(entry.url)
            elif action == "open_url" and entry.url:
                import webbrowser

                webbrowser.open(entry.url)
        except Exception as e:
            logger.error(f"Error handling action {action}: {e}")

    def exit_application(self):
        """Exit the application."""
        logger.info("Exiting application...")
        self._release_mutex()
        sys.exit(0)

    def run(self):
        """Run the application."""
        try:
            # Create and run window without connecting to database immediately
            self.window = SearchWindow(
                self.handle_search,
                self.handle_action,
                self.handle_select,
                self.db_manager.lazy_connect_database,  # Callback for lazy connection
                self.search_service.get_recent_entries,  # Callback for getting recent entries
            )

            # Wire up managers to window and state manager
            self.db_manager.window = self.window
            self.db_manager.state_manager = self.window.state_manager
            self.lock_manager.window = self.window
            self.lock_manager.state_manager = self.window.state_manager

            # Override the exit handler to use our method
            self.window._handle_exit = self.exit_application

            # Set the reload handler
            self.window.reload_handler = self.db_manager.reload_database

            # Start idle time checking
            self.lock_manager.check_idle_time()

            hotkey = config.get_search_hotkey()
            idle_timeout = config.get_database_idle_timeout()
            logger.info(f"KeePass Data Retriever running. Press {hotkey} to open search window.")
            logger.info("Right-click the window for menu options.")
            logger.info(f"Database will lock after {idle_timeout} seconds of inactivity.")
            logger.info("Type /exit in any search box to exit the application.")
            logger.info("Type /reload in any search box to reload the database.")

            self.window.run()

        except KeyboardInterrupt:
            logger.info("Exiting...")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)
        finally:
            self._release_mutex()


def main():
    app = KeePassRetriever()
    app.run()


if __name__ == "__main__":
    main()
