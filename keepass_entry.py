from pykeepass import PyKeePass
from typing import Optional, List

class KeePassEntryManager:
    def __init__(self, db_path: str, db_password: str):
        self.kp = PyKeePass(db_path, password=db_password)

    def search(self, search_term: str) -> List['PyKeePass.Entry']:
        """Search for entries in the database"""
        entries = []
        search_terms = search_term.lower().split()
        
        # Search through all entries
        for entry in self.kp.entries:
            title = (entry.title or "").lower()
            username = (entry.username or "").lower()
            
            # Check if all search terms are found in either title or username
            if all(term in title or term in username for term in search_terms):
                entries.append(entry)
        
        # Return first 9 entries
        return entries[:9]
