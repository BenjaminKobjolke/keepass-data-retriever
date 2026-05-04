"""Database locking and idle timeout management."""

import win32api
from config import config
from services.password_provider import PasswordProvider
from ui.state_manager import AppState


class DatabaseLockManager:
    """Manages database locking based on system idle time."""

    def __init__(self, database_manager):
        """
        Initialize lock manager.

        Args:
            database_manager: DatabaseManager instance to control
        """
        self.database_manager = database_manager
        self.idle_timeout = config.get_database_idle_timeout()
        self.window = None  # Will be set by main application
        self.state_manager = None  # Will be set by main application

    def check_idle_time(self):
        """Check system idle time and lock if necessary."""
        try:
            # Get last input info
            last_input = win32api.GetLastInputInfo()
            idle_time = (win32api.GetTickCount() - last_input) / 1000.0  # Convert to seconds

            if idle_time >= self.idle_timeout and not self.database_manager.is_locked:
                print(f"System idle for {idle_time:.1f} seconds - locking database")
                # Lock database
                self.database_manager.lock()

                # Transition to LOCKED state if state manager exists
                if self.state_manager:
                    self.state_manager.transition_to(AppState.LOCKED)

            # Schedule next check
            if self.window and self.window.root:
                self.window.root.after(1000, self.check_idle_time)  # Check every second

        except Exception as e:
            print(f"Error checking idle time: {e}")

    def lock_database(self):
        """
        Lock the database and show password dialog for unlocking.

        Returns:
            bool: True if unlocked successfully, False otherwise
        """
        # Lock the database
        self.database_manager.lock()

        # Transition to LOCKED state if state manager exists
        if self.state_manager:
            self.state_manager.transition_to(AppState.LOCKED)

        # Show password dialog
        password = PasswordProvider.get_password()
        if password:
            if self.database_manager.unlock(password):
                # Transition back to INITIAL state if state manager exists
                if self.state_manager:
                    self.state_manager.transition_to(AppState.INITIAL)
                return True
            else:
                # Try again if unlock failed
                return self.lock_database()
        else:
            print("Password input cancelled")
            return False
