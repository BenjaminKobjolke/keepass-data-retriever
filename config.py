#!/usr/bin/env python3

import os
import configparser
import re
from typing import Optional, Tuple

class Config:
    """Configuration handler for KeePass Data Retriever"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = 'settings.ini'
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from settings.ini file"""
        # Set default values
        self.config['General'] = {
            'search_reset_timeout': '180',  # 3 minutes in seconds
            'database_idle_timeout': '3600',  # 1 hour in seconds
            'database_path': 'Database.kdbx',  # Default database path
            'debug_mode': 'false'  # Debug mode disabled by default
        }
        self.config['Hotkeys'] = {
            'search_hotkey': 'alt + shift + F8'
        }
        
        # Read from file if it exists
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
            except Exception as e:
                print(f"Error reading config file: {e}")
    
    def get_search_reset_timeout(self) -> int:
        """Get search reset timeout in seconds"""
        try:
            return int(self.config.get('General', 'search_reset_timeout'))
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return 180  # Default: 3 minutes
    
    def get_search_hotkey(self) -> str:
        """Get search hotkey combination"""
        default_hotkey = 'alt + shift + F8'
        
        try:
            hotkey = self.config.get('Hotkeys', 'search_hotkey')
            return hotkey
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default_hotkey  # Default hotkey
    
    def get_database_idle_timeout(self) -> int:
        """Get database idle timeout in seconds"""
        try:
            return int(self.config.get('General', 'database_idle_timeout'))
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return 3600  # Default: 1 hour
    
    def get_database_path(self) -> str:
        """Get database path from config"""
        try:
            return self.config.get('General', 'database_path')
        except (configparser.NoSectionError, configparser.NoOptionError):
            return 'Database.kdbx'  # Default fallback
            
    def get_debug_mode(self) -> bool:
        """Get debug mode from config"""
        try:
            debug_mode = self.config.get('General', 'debug_mode').lower()
            return debug_mode in ('true', 'yes', '1', 'on')
        except (configparser.NoSectionError, configparser.NoOptionError):
            return False  # Default: debug mode disabled

# Create a singleton instance
config = Config()
