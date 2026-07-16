"""Typed theme color palette — single source of color names, defaults, and labels.

Consumers must derive color-name lists from this class (see color_names()/labels())
instead of hardcoding key lists.
"""

from dataclasses import asdict, dataclass, field, fields


@dataclass(frozen=True)
class ThemeColors:
    """The application's theme color palette (defaults = dark theme)."""

    bg_color: str = field(default="#1e1e1e", metadata={"label": "Background"})
    fg_color: str = field(default="#ffffff", metadata={"label": "Text"})
    entry_bg: str = field(default="#2d2d2d", metadata={"label": "Input Background"})
    entry_fg: str = field(default="#ffffff", metadata={"label": "Input Text"})
    button_bg: str = field(default="#3d3d3d", metadata={"label": "Button Background"})
    button_fg: str = field(default="#ffffff", metadata={"label": "Button Text"})
    highlight_bg: str = field(default="#2E2E2E", metadata={"label": "Highlight"})
    recent_entry_bg: str = field(default="#063970", metadata={"label": "Recent Entry"})
    action_highlight_bg: str = field(default="#5a5a5a", metadata={"label": "Action Highlight"})
    button_hover_bg: str = field(default="#4d4d4d", metadata={"label": "Button Hover"})

    @classmethod
    def color_names(cls) -> list[str]:
        """All color field names, in declaration order."""
        return [f.name for f in fields(cls)]

    @classmethod
    def labels(cls) -> dict[str, str]:
        """Color name -> human-readable display label."""
        return {f.name: f.metadata["label"] for f in fields(cls)}

    @classmethod
    def defaults(cls) -> dict[str, str]:
        """Color name -> default value."""
        return asdict(cls())

    def as_dict(self) -> dict[str, str]:
        """Plain dict view for internal/Tk-facing use."""
        return asdict(self)
