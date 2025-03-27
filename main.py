#!/usr/bin/env python3

import sys
import os
import uuid
from pykeepass import PyKeePass
import pyperclip
import time
import win32api
import win32con
from ui.search_window import SearchWindow
from ui.password_dialog import PasswordDialog
from ui.state_manager import AppState
from config import config

class KeePassRetriever:
    def __init__(self):
        self.kp = None
        self.window = None
        self.last_activity_time = time.time()
        self.idle_timeout = config.get_database_idle_timeout()
        self.is_locked = False

    def get_database_path(self):
        """Get database path from settings, command line, environment, or default"""
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

    def get_password(self):
        """Get password using GUI dialog"""
        args = sys.argv[1:]
        
        # Check for --password argument
        for i, arg in enumerate(args):
            if arg == '--password' and i + 1 < len(args):
                return args[i + 1]
        
        # If no password provided, show password dialog
        dialog = PasswordDialog()
        return dialog.get_password()

    def connect_database(self):
        """Connect to KeePass database"""
        try:
            db_path = self.get_database_path()
            if not os.path.exists(db_path):
                print(f"Error: Database file not found: {db_path}")
                print("Configure database_path in settings.ini, use --database argument, or set KEEPASS_DATABASE environment variable")
                return False

            password = self.get_password()
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

    def check_idle_time(self):
        """Check system idle time and lock if necessary"""
        try:
            # Get last input info
            last_input = win32api.GetLastInputInfo()
            idle_time = (win32api.GetTickCount() - last_input) / 1000.0  # Convert to seconds
            
            if idle_time >= self.idle_timeout and not self.is_locked:
                print(f"System idle for {idle_time:.1f} seconds - locking database")
                # Lock database, but don't exit if user cancels
                self.is_locked = True
                self.kp = None  # Clear the database connection
                
                # Transition to LOCKED state if window exists
                if self.window and hasattr(self.window, 'state_manager'):
                    self.window.state_manager.transition_to(AppState.LOCKED)
            
            # Schedule next check
            if self.window and self.window.root:
                self.window.root.after(1000, self.check_idle_time)  # Check every second
                
        except Exception as e:
            print(f"Error checking idle time: {e}")

    def lock_database(self):
        """Lock the database and show password dialog"""
        self.is_locked = True
        self.kp = None  # Clear the database connection
        
        # Transition to LOCKED state if window exists
        if self.window and hasattr(self.window, 'state_manager'):
            self.window.state_manager.transition_to(AppState.LOCKED)
        
        # Show password dialog
        password = self.get_password()
        if password:
            try:
                db_path = self.get_database_path()
                self.kp = PyKeePass(db_path, password)
                self.is_locked = False
                print("Database unlocked successfully")
                
                # Transition back to INITIAL state if window exists
                if self.window and hasattr(self.window, 'state_manager'):
                    self.window.state_manager.transition_to(AppState.INITIAL)
                
                return True
            except Exception as e:
                print(f"Error unlocking database: {e}")
                # Try again if unlock failed
                return self.lock_database()
        else:
            print("Password input cancelled")
            return False

    def handle_search(self, search_term):
        """Handle search request"""
        if self.is_locked:
            return
            
        entries = []
        # Split search term into individual words
        search_terms = search_term.lower().split()
        
        for entry in self.kp.entries:
            title = (entry.title or "").lower()
            username = (entry.username or "").lower()
            
            # Replace hyphens with spaces to improve matching
            searchable_title = title.replace('-', ' ')
            searchable_username = username.replace('-', ' ')
            
            # Check if all search terms are found in either title or username
            if all(term in searchable_title or term in searchable_username for term in search_terms):
                entries.append(entry)
                
        self.window.show_entries(entries)

    def handle_select(self, entry):
        """Handle entry selection"""
        if self.is_locked:
            return
        self.window.show_selected_entry(entry)

    def handle_action(self, action, entry=None):
        """Handle action request"""
        if self.is_locked:
            return
            
        if not entry:
            entry = self.window.input.single_entry
        if not entry:
            print("No entry selected")
            return
            
        try:
            if action == 'username' and entry.username:
                pyperclip.copy(entry.username)
            elif action == 'password' and entry.password:
                pyperclip.copy(entry.password)
            elif action == 'url' and entry.url:
                pyperclip.copy(entry.url)
            elif action == 'open_url' and entry.url:
                import webbrowser
                webbrowser.open(entry.url)
        except Exception as e:
            print(f"Error handling action {action}: {e}")
            
    def find_entries_by_uuids(self, uuids):
        """Find entries by their UUIDs"""
        if self.is_locked or not self.kp:
            return []
            
        entries = []
        for uuid_str in uuids:
            try:
                # Convert string UUID to UUID object
                uuid_obj = uuid.UUID(uuid_str)
                
                # Use PyKeePass's find_entries method with the uuid parameter
                entry = self.kp.find_entries(uuid=uuid_obj, first=True)
                if entry:
                    entries.append(entry)
            except Exception as e:
                print(f"Error finding entry with UUID {uuid_str}: {e}")
        
        return entries
        
    def get_recent_entries(self, entry_ids):
        """Get entries by their UUIDs"""
        if self.is_locked:
            return []
        
        return self.find_entries_by_uuids(entry_ids)

    def lazy_connect_database(self):
        """Connect to database if not already connected"""
        if self.kp is None or self.is_locked:
            return self.connect_database()
        return True  # Already connected

    def exit_application(self):
        """Exit the application"""
        print("\nExiting application...")
        sys.exit(0)
        
    def run(self):
        """Run the application"""
        try:
            # Create and run window without connecting to database immediately
            self.window = SearchWindow(
                self.handle_search,
                self.handle_action,
                self.handle_select,
                self.lazy_connect_database,  # Callback for lazy connection
                self.get_recent_entries  # Callback for getting recent entries
            )
            
            # Override the exit handler to use our method
            self.window._handle_exit = self.exit_application
            
            # Start idle time checking
            self.check_idle_time()
            
            hotkey = config.get_search_hotkey()
            print(f"KeePass Data Retriever running. Press {hotkey} to open search window.")
            print("Right-click the window for menu options.")
            print(f"Database will lock after {self.idle_timeout} seconds of inactivity.")
            print("Type /exit in any search box to exit the application.")
            
            self.window.run()

        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

def main():
    app = KeePassRetriever()
    app.run()

if __name__ == '__main__':
    main()
