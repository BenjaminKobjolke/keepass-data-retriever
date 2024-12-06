import sys
import argparse
import pyperclip
import webbrowser
from keepass_entry import KeePassEntryManager
from ui import SearchWindow
from typing import Optional

class KeePassSearch:
    def __init__(self, db_path: str, db_password: str):
        self.entry_manager = KeePassEntryManager(db_path, db_password)
        self.current_entry = None
        self.last_search_term = ""
        
        # Create window with callbacks
        self.window = SearchWindow(
            on_search=self.handle_search,
            on_action=self.handle_action,
            on_select=self.handle_select
        )

    def handle_search(self, search_term: str):
        """Handle search request"""
        if not search_term:
            return
            
        try:
            # Save search term
            self.last_search_term = search_term
            
            # Search for entries
            entries = self.entry_manager.search(search_term)
            
            if entries:
                # Show list of entries
                self.window.show_entries(entries)
                if len(entries) == 1:
                    self.current_entry = entries[0]
            else:
                self.current_entry = None
                self.window.show_entries([])
                
        except Exception as e:
            self.window.set_status(f"Error: {str(e)}")

    def handle_select(self, entry: 'PyKeePass.Entry'):
        """Handle entry selection"""
        self.current_entry = entry
        self.window.show_selected_entry(entry)

    def handle_action(self, action: str):
        """Handle action request"""
        if not self.current_entry:
            return
            
        if action == 'username':
            pyperclip.copy(self.current_entry.username or "")
            self.window.set_status("Username copied")
        elif action == 'password':
            pyperclip.copy(self.current_entry.password or "")
            self.window.set_status("Password copied")
        elif action == 'url':
            pyperclip.copy(self.current_entry.url or "")
            self.window.set_status("URL copied")
        elif action == 'open_url':
            if self.current_entry.url:
                webbrowser.open(self.current_entry.url)
                self.window.set_status("Opening URL")
            else:
                self.window.set_status("No URL available")
        
        # Hide window
        self.window.hide()

    def run(self):
        """Start the application"""
        self.window.run()

def main():
    parser = argparse.ArgumentParser(description='KeePass Search GUI')
    parser.add_argument('--db', default='db.kdbx', help='Path to KeePass database')
    parser.add_argument('--password', required=True, help='Database password')
    args = parser.parse_args()
    
    try:
        app = KeePassSearch(args.db, args.password)
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
