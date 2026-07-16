"""Constants for the KeePass Data Retriever UI."""

APP_NAME = "Keepass-Retriever"


class Actions:
    """Action type identifiers."""

    AUTO_TYPE = "auto_type"
    USERNAME = "username"
    PASSWORD = "password"
    TYPE_USERNAME = "type_username"
    TYPE_PASSWORD = "type_password"
    URL = "url"
    OPEN_URL = "open_url"


class Fonts:
    """Font definitions."""

    NORMAL = ("Segoe UI", 11)
    SMALL = ("Segoe UI", 10)


class Styles:
    """TTK style names."""

    # Dark theme base styles
    DARK_FRAME = "Dark.TFrame"
    DARK_LABEL = "Dark.TLabel"

    # Highlighted styles
    HIGHLIGHTED_FRAME = "Highlighted.TFrame"
    HIGHLIGHTED_LABEL = "Highlighted.TLabel"
    HIGHLIGHTED_URL_LABEL = "HighlightedURL.TLabel"

    # Recent entry styles
    RECENT_ENTRY_FRAME = "RecentEntry.TFrame"
    RECENT_ENTRY_LABEL = "RecentEntry.TLabel"
    RECENT_ENTRY_URL_LABEL = "RecentEntryURL.TLabel"

    # Highlighted recent entry styles
    HIGHLIGHTED_RECENT_FRAME = "HighlightedRecentEntry.TFrame"
    HIGHLIGHTED_RECENT_LABEL = "HighlightedRecentEntry.TLabel"
    HIGHLIGHTED_RECENT_URL_LABEL = "HighlightedRecentEntryURL.TLabel"
