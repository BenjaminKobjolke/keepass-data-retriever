"""Database connection and lifecycle management for KeePass."""

import os
import sys
from pykeepass import PyKeePass
from config import config
from services.password_provider import PasswordProvider
from ui.state_manager import AppState


class DatabaseManager:
    """Manages KeePass database connection, path resolution, and reload operations."""

    def __init__(self):
        """Initialize database manager."""
        self.kp = None
        self.is_locked = False
        self.window = None  # Will be set by main application
        self.state_manager = None  # Will be set by main application

    def get_database_path(self):
        """
        Get database path from settings, command line, environment, or default.

        Returns:
            str: Path to the database file
        """
        # First check settings.ini
        db_path = config.get_database_path()
        if db_path and os.path.exists(db_path):
            return db_path

        # Check for --database argument (for backward compatibility)
        args = sys.argv[1:]
        for i, arg in enumerate(args):
            if arg == '--database' and i + 1 < len(args):
                return args[i + 1]

        # Check environment variable (for backward compatibility)
        if env_path := os.getenv('KEEPASS_DATABASE'):
            return env_path

        # Use default
        return 'Database.kdbx'

    def connect_database(self):
        """
        Connect to KeePass database.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            db_path = self.get_database_path()
            if not os.path.exists(db_path):
                print(f"Error: Database file not found: {db_path}")
                print("Configure database_path in settings.ini, use --database argument, or set KEEPASS_DATABASE environment variable")
                return False

            password = PasswordProvider.get_password()
            if not password:  # User cancelled the dialog
                print("Password input cancelled")
                return False

            self.kp = PyKeePass(db_path, password)
            self.is_locked = False
            print(f"Successfully connected to KeePass database: {db_path}")
            return True
        except Exception as e:
            print(f"Error opening KeePass database: {e}")
            return False

    def lazy_connect_database(self):
        """
        Connect to database if not already connected.

        Returns:
            bool: True if connected (or already connected), False otherwise
        """
        if self.kp is None or self.is_locked:
            return self.connect_database()
        return True  # Already connected

    def _do_reload(self):
        """
        Perform the actual reload operation.

        Returns:
            bool: True if reload successful, False otherwise
        """
        try:
            # Get database path
            db_path = self.get_database_path()
            if not os.path.exists(db_path):
                print(f"Error: Database file not found: {db_path}")
                return False

            # Always prompt for password on reload
            password = PasswordProvider.get_password_for_reload()
            if not password:  # User cancelled the dialog
                print("Password input cancelled")
                return False

            self.kp = PyKeePass(db_path, password)
            self.is_locked = False
            print("Database reloaded successfully")

            # Transition back to INITIAL state if state manager exists
            if self.state_manager:
                self.state_manager.transition_to(AppState.INITIAL)
            return True
        except Exception as e:
            print(f"Error reloading database: {e}")
            return False

    def reload_database(self):
        """Reload the KeePass database."""
        print("\nReloading database...")
        # Clear current database connection
        self.kp = None
        self.is_locked = False

        # Schedule the dialog to show after current event processing completes
        if self.window and self.window.root:
            self.window.root.after(100, self._do_reload)
        else:
            self._do_reload()

    def lock(self):
        """Lock the database (clear connection)."""
        self.is_locked = True
        self.kp = None

    def unlock(self, password):
        """
        Unlock the database with provided password.

        Args:
            password: Password to unlock database

        Returns:
            bool: True if unlock successful, False otherwise
        """
        try:
            db_path = self.get_database_path()
            self.kp = PyKeePass(db_path, password)
            self.is_locked = False
            print("Database unlocked successfully")
            return True
        except Exception as e:
            print(f"Error unlocking database: {e}")
            return False
