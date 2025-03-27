import logging
from typing import Optional
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class Logger:
    """Centralized logging class for the application"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance
    
    def __init__(self):
        """Initialize the logger"""
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('keepass_data_retriever')
        
        # Get debug mode from config
        self.debug_enabled = config.get_debug_mode()
        
        # Set log level based on debug mode
        if self.debug_enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
    
    def debug(self, message: str):
        """Log a debug message"""
        if self.debug_enabled:
            self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log a critical message"""
        self.logger.critical(message)
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        return self.debug_enabled
        
    def set_debug(self, enabled: bool):
        """Set debug mode"""
        self.debug_enabled = enabled
        if enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
