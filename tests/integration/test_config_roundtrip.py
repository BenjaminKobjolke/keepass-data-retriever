"""Integration tests: Config <-> settings.ini <-> ThemeColors round-trips on real files."""

import pytest

from theme_colors import ThemeColors


@pytest.fixture
def tmp_cwd(tmp_path, monkeypatch):
    """Isolate each test in an empty working directory (Config uses relative settings.ini)."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _fresh_config():
    from config import Config

    return Config()


def test_general_settings_roundtrip_through_real_ini(tmp_cwd):
    (tmp_cwd / "settings.ini").write_text(
        "[General]\n"
        "database_path = C:/dbs/test.kdbx\n"
        "search_reset_timeout = 42\n"
        "database_idle_timeout = 900\n"
        "debug_mode = true\n"
        "[Hotkeys]\n"
        "search_hotkey = ctrl + alt + F9\n",
        encoding="utf-8",
    )
    cfg = _fresh_config()
    assert cfg.get_database_path() == "C:/dbs/test.kdbx"
    assert cfg.get_search_reset_timeout() == 42
    assert cfg.get_database_idle_timeout() == 900
    assert cfg.get_debug_mode() is True
    assert cfg.get_search_hotkey() == "ctrl + alt + F9"


def test_theme_palette_roundtrip_through_real_ini(tmp_cwd):
    cfg = _fresh_config()
    custom = ThemeColors(bg_color="#101010", button_bg="#aabbcc")
    cfg.set_all_theme_colors(custom)
    cfg.set_theme_preset("custom")
    cfg.save_config()

    reloaded = _fresh_config()
    palette = reloaded.get_all_theme_colors()
    assert isinstance(palette, ThemeColors)
    assert palette.bg_color == "#101010"
    assert palette.button_bg == "#aabbcc"
    assert palette.fg_color == ThemeColors().fg_color  # untouched field keeps default
    assert reloaded.get_theme_preset() == "custom"


def test_missing_ini_yields_full_default_palette(tmp_cwd):
    cfg = _fresh_config()
    assert cfg.get_all_theme_colors() == ThemeColors()
