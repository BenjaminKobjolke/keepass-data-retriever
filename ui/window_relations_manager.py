import json
import os
import win32gui
import time
from typing import List, Optional, Any

class WindowRelationsManager:
    def __init__(self, file_path: str = "window-relations.json"):
        self.file_path = file_path
        self.relations = self._load_relations()
        self.current_window_title = None
    
    def _load_relations(self) -> List:
        """Load existing relations from JSON file or create new structure"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading window relations: {e}")
                return []
        return []  # Return empty array instead of empty dict
    
    def _save_relations(self) -> None:
        """Save relations to JSON file"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.relations, f, indent=2)
        except Exception as e:
            print(f"Error saving window relations: {e}")
    
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
                self.current_window_title = window_title
                
                # Find window in relations
                window_index = self._find_window_index(window_title)
                
                if window_index == -1:
                    # Window not found, add it
                    self.relations.append({
                        "title": window_title,
                        "count": 1,
                        "last_accessed": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "recent_entries": []  # List to store the last 3 entry IDs
                    })
                else:
                    # Window found, update it
                    self.relations[window_index]["count"] += 1
                    self.relations[window_index]["last_accessed"] = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Save to file
                self._save_relations()
                return window_title
            
            return None
        except Exception as e:
            print(f"Error logging active window: {e}")
            return None
    
    def log_entry_selection(self, entry: Any) -> None:
        """Log the selected KeePass entry for the current window"""
        if not self.current_window_title or not entry:
            return
        
        try:
            # Get entry ID - assuming entry has an 'uuid' attribute
            # If not, we'll need to use another unique identifier
            entry_id = str(entry.uuid) if hasattr(entry, 'uuid') else str(id(entry))
            
            # Find window in relations
            window_index = self._find_window_index(self.current_window_title)
            if window_index == -1:
                return
            
            # Get the window data
            window_data = self.relations[window_index]
            
            # Get the recent entries list
            recent_entries = window_data.get("recent_entries", [])
            
            # Remove this entry if it already exists in the list
            if entry_id in recent_entries:
                recent_entries.remove(entry_id)
            
            # Add the entry to the beginning of the list
            recent_entries.insert(0, entry_id)
            
            # Keep only the last 3 entries
            window_data["recent_entries"] = recent_entries[:3]
            
            # Save to file
            self._save_relations()
        except Exception as e:
            print(f"Error logging entry selection: {e}")
    
    def get_recent_entries_for_current_window(self) -> List[str]:
        """Get recent entry IDs for the current window"""
        if not self.current_window_title:
            return []
        
        window_index = self._find_window_index(self.current_window_title)
        if window_index == -1:
            return []
        
        return self.relations[window_index].get("recent_entries", [])
