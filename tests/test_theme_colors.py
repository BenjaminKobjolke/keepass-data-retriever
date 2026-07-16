"""Characterization tests for theme color configuration.

Pin the theme-color contract before/after the ThemeColors refactor:
same 10 color names, same default values, config round-trip works.
"""

import os

import pytest

EXPECTED_DEFAULTS = {
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
}


@pytest.fixture
def fresh_config(tmp_path, monkeypatch):
    """Config instance reading/writing settings.ini in an isolated tmp cwd."""
    monkeypatch.chdir(tmp_path)
    from config import Config

    return Config()


def _as_dict(colors):
    """Accept both the legacy dict and the typed ThemeColors object."""
    if isinstance(colors, dict):
        return colors
    from dataclasses import asdict

    return asdict(colors)


def test_all_theme_colors_have_expected_names_and_defaults(fresh_config):
    colors = _as_dict(fresh_config.get_all_theme_colors())
    assert colors == EXPECTED_DEFAULTS


def test_single_color_lookup_falls_back_to_default(fresh_config):
    assert fresh_config.get_theme_color("recent_entry_bg") == "#063970"
    assert fresh_config.get_theme_color("nonexistent") == "#1e1e1e"


def test_set_color_round_trips_through_ini(fresh_config, tmp_path):
    fresh_config.set_theme_color("bg_color", "#123456")
    fresh_config.save_config()
    assert os.path.exists(tmp_path / "settings.ini")

    from config import Config

    reloaded = Config()
    assert reloaded.get_theme_color("bg_color") == "#123456"
    colors = _as_dict(reloaded.get_all_theme_colors())
    assert colors["bg_color"] == "#123456"
    assert colors["fg_color"] == "#ffffff"
