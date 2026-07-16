#!/usr/bin/env python3

import os
import configparser
import logging

from theme_colors import ThemeColors


class Config:
    """Configuration handler for KeePass Data Retriever"""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = "settings.ini"

        # Load configuration
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from settings.ini file"""
        # Set default values
        self.config["General"] = {
            "search_reset_timeout": "180",  # 3 minutes in seconds
            "database_idle_timeout": "3600",  # 1 hour in seconds
            "database_path": "Database.kdbx",  # Default database path
            "debug_mode": "false",  # Debug mode disabled by default
            "window_position": "mouse",  # Window position mode: 'mouse', 'center', or 'center_screen'
            "paste_mode": "true",  # Use paste instead of typing (avoids dead key issues)
            "window_width": "500",  # Window width in pixels
        }
        self.config["Hotkeys"] = {"search_hotkey": "alt + shift + F8"}
        self.config["Theme"] = {
            "preset": "dark",  # 'dark', 'light', or 'custom'
            "bg_color": "#1e1e1e",
            "fg_color": "#ffffff",
            "entry_bg": "#2d2d2d",
            "entry_fg": "#ffffff",
            "button_bg": "#3d3d3d",
            "button_fg": "#ffffff",
            "highlight_bg": "#2E2E2E",
            "recent_entry_bg": "#063970",
            "action_highlight_bg": "#5a5a5a",
            "button_hover_bg": "#4d4d4d",
            "transparency": "0.9",
        }

        # Read from file if it exists
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
            except Exception as e:
                # ponytail: direct logging call — ui.logger.Logger imports this module
                # at load time, so importing it here would recurse during module init
                logging.getLogger("keepass_data_retriever").error(f"Error reading config file: {e}")

    def get_search_reset_timeout(self) -> int:
        """Get search reset timeout in seconds"""
        try:
            return int(self.config.get("General", "search_reset_timeout"))
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return 180  # Default: 3 minutes

    def get_search_hotkey(self) -> str:
        """Get search hotkey combination"""
        default_hotkey = "alt + shift + F8"

        try:
            hotkey = self.config.get("Hotkeys", "search_hotkey")
            return hotkey
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default_hotkey  # Default hotkey

    def get_database_idle_timeout(self) -> int:
        """Get database idle timeout in seconds"""
        try:
            return int(self.config.get("General", "database_idle_timeout"))
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return 3600  # Default: 1 hour

    def get_database_path(self) -> str:
        """Get database path from config"""
        try:
            return self.config.get("General", "database_path")
        except (configparser.NoSectionError, configparser.NoOptionError):
            return "Database.kdbx"  # Default fallback

    def get_debug_mode(self) -> bool:
        """Get debug mode from config"""
        try:
            debug_mode = self.config.get("General", "debug_mode").lower()
            return debug_mode in ("true", "yes", "1", "on")
        except (configparser.NoSectionError, configparser.NoOptionError):
            return False  # Default: debug mode disabled

    def get_window_position_mode(self) -> str:
        """Get window position mode from config"""
        try:
            mode = self.config.get("General", "window_position").lower()
            if mode in ("mouse", "center", "center_screen"):
                return mode
            return "mouse"  # Default if invalid value
        except (configparser.NoSectionError, configparser.NoOptionError):
            return "mouse"  # Default: position at mouse cursor

    def get_paste_mode(self) -> bool:
        """Get paste mode from config - when true, use clipboard paste instead of typing"""
        try:
            paste_mode = self.config.get("General", "paste_mode").lower()
            return paste_mode in ("true", "yes", "1", "on")
        except (configparser.NoSectionError, configparser.NoOptionError):
            return True  # Default: paste mode enabled (avoids dead key issues)

    def get_window_width(self) -> int:
        """Get window width in pixels"""
        try:
            width = int(self.config.get("General", "window_width"))
            return max(350, min(width, 800))
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return 500

    def get_theme_preset(self) -> str:
        """Get current theme preset name"""
        try:
            return self.config.get("Theme", "preset").lower()
        except (configparser.NoSectionError, configparser.NoOptionError):
            return "dark"

    def set_theme_preset(self, preset: str) -> None:
        """Set theme preset"""
        if "Theme" not in self.config:
            self.config["Theme"] = {}
        self.config["Theme"]["preset"] = preset

    def get_theme_color(self, color_name: str) -> str:
        """Get a theme color by name"""
        try:
            return self.config.get("Theme", color_name)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return ThemeColors.defaults().get(color_name, "#1e1e1e")

    def set_theme_color(self, color_name: str, value: str) -> None:
        """Set a theme color"""
        if "Theme" not in self.config:
            self.config["Theme"] = {}
        self.config["Theme"][color_name] = value

    def get_theme_transparency(self) -> float:
        """Get theme transparency value"""
        try:
            return float(self.config.get("Theme", "transparency"))
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return 0.9

    def set_theme_transparency(self, value: float) -> None:
        """Set theme transparency value"""
        if "Theme" not in self.config:
            self.config["Theme"] = {}
        self.config["Theme"]["transparency"] = str(value)

    def get_all_theme_colors(self) -> ThemeColors:
        """Get all theme colors as a typed palette"""
        return ThemeColors(
            **{name: self.get_theme_color(name) for name in ThemeColors.color_names()}
        )

    def set_all_theme_colors(self, colors: ThemeColors) -> None:
        """Set all theme colors from a typed palette"""
        for name, value in colors.as_dict().items():
            self.set_theme_color(name, value)

    def save_config(self) -> None:
        """Save configuration to settings.ini"""
        try:
            with open(self.config_path, "w") as configfile:
                self.config.write(configfile)
        except Exception as e:
            # ponytail: direct logging call — see load-time note above
            logging.getLogger("keepass_data_retriever").error(f"Error saving config file: {e}")


# Create a singleton instance
config = Config()
