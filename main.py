#!/usr/bin/env python3

import sys
import os
from pykeepass import PyKeePass
import pyperclip
import time
import win32api
import win32con
from ui.search_window import SearchWindow
from ui.password_dialog import PasswordDialog

class KeePassRetriever:
    def __init__(self):
        self.kp = None
        self.window = None
        self.last_activity_time = time.time()
        self.idle_timeout = 1 * 60 * 60 # 1 hour 
        #self.idle_timeout = 10 # 10 seconds
        self.is_locked = False

    def get_database_path(self):
        """Get database path from command line, environment, or default"""
        args = sys.argv[1:]
        
        # Check for --database argument
        for i, arg in enumerate(args):
            if arg == '--database' and i + 1 < len(args):
                return args[i + 1]
        
        # Check environment variable
        if db_path := os.getenv('KEEPASS_DATABASE'):
            return db_path
            
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
                print("Use --database argument or set KEEPASS_DATABASE environment variable")
                sys.exit(1)

            password = self.get_password()
            if not password:  # User cancelled the dialog
                print("Password input cancelled")
                sys.exit(1)
                
            self.kp = PyKeePass(db_path, password)
            self.is_locked = False
            print(f"Successfully connected to KeePass database: {db_path}")
        except Exception as e:
            print(f"Error opening KeePass database: {e}")
            sys.exit(1)

    def check_idle_time(self):
        """Check system idle time and lock if necessary"""
        try:
            # Get last input info
            last_input = win32api.GetLastInputInfo()
            idle_time = (win32api.GetTickCount() - last_input) / 1000.0  # Convert to seconds
            
            if idle_time >= self.idle_timeout and not self.is_locked:
                print(f"System idle for {idle_time:.1f} seconds - locking database")
                self.lock_database()
            
            # Schedule next check
            if self.window and self.window.root:
                self.window.root.after(1000, self.check_idle_time)  # Check every second
                
        except Exception as e:
            print(f"Error checking idle time: {e}")

    def lock_database(self):
        """Lock the database and show password dialog"""
        self.is_locked = True
        self.kp = None  # Clear the database connection
        
        # Show password dialog
        password = self.get_password()
        if password:
            try:
                db_path = self.get_database_path()
                self.kp = PyKeePass(db_path, password)
                self.is_locked = False
                print("Database unlocked successfully")
            except Exception as e:
                print(f"Error unlocking database: {e}")
                # Try again if unlock failed
                self.lock_database()
        else:
            print("Password input cancelled - exiting")
            sys.exit(1)

    def handle_search(self, search_term):
        """Handle search request"""
        if self.is_locked:
            return
            
        entries = []
        for entry in self.kp.entries:
            if (entry.title and search_term.lower() in entry.title.lower()) or \
               (entry.username and search_term.lower() in entry.username.lower()):
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
            elif action == 'paste_username' and entry.username:
                pyperclip.copy(entry.username)
            elif action == 'paste_password' and entry.password:
                pyperclip.copy(entry.password)
        except Exception as e:
            print(f"Error handling action {action}: {e}")

    def run(self):
        """Run the application"""
        try:
            # Connect to database
            self.connect_database()

            # Create and run window
            self.window = SearchWindow(
                self.handle_search,
                self.handle_action,
                self.handle_select
            )
            
            # Start idle time checking
            self.check_idle_time()
            
            print("KeePass Data Retriever running. Press Alt+Shift+F8 to open search window.")
            print("Right-click the window for menu options.")
            print(f"Database will lock after {self.idle_timeout} seconds of inactivity.")
            
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
