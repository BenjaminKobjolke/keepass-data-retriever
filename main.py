#!/usr/bin/env python3

import sys
import os
import getpass
from pykeepass import PyKeePass
import pyperclip
from ui.search_window import SearchWindow

class KeePassRetriever:
    def __init__(self):
        self.kp = None
        self.window = None

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
        """Get password from command line or prompt"""
        args = sys.argv[1:]
        
        # Check for --password argument
        for i, arg in enumerate(args):
            if arg == '--password' and i + 1 < len(args):
                return args[i + 1]
        
        # If no password provided, prompt for it
        return getpass.getpass('Enter KeePass password: ')

    def connect_database(self):
        """Connect to KeePass database"""
        try:
            db_path = self.get_database_path()
            if not os.path.exists(db_path):
                print(f"Error: Database file not found: {db_path}")
                print("Use --database argument or set KEEPASS_DATABASE environment variable")
                sys.exit(1)

            password = self.get_password()
            self.kp = PyKeePass(db_path, password)
            print(f"Successfully connected to KeePass database: {db_path}")
        except Exception as e:
            print(f"Error opening KeePass database: {e}")
            sys.exit(1)

    def handle_search(self, search_term):
        """Handle search request"""
        entries = []
        for entry in self.kp.entries:
            if (entry.title and search_term.lower() in entry.title.lower()) or \
               (entry.username and search_term.lower() in entry.username.lower()):
                entries.append(entry)
        self.window.show_entries(entries)

    def handle_select(self, entry):
        """Handle entry selection"""
        self.window.show_selected_entry(entry)

    def handle_action(self, action):
        """Handle action request"""
        entry = self.window.input.single_entry
        if not entry:
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
            print("KeePass Data Retriever running. Press Alt+Shift+R to open search window.")
            print("Right-click the window for menu options.")
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
