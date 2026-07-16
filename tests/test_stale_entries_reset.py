"""Regression tests for stale ghost suggestions after window context switch.

Bug: after hiding the window and reopening it on a window with no recent
entries, BackSpace re-rendered the previous window's entries because
InputManager.original_entries survived the INITIAL reset.
"""

import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace

import pytest

from ui.events import EventBus, Events
from ui.input.input_manager import InputManager
from ui.status_display import StatusDisplay


# ponytail: module-scoped root — Tk re-creation after destroy is flaky on Windows
@pytest.fixture(scope="module")
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No display available for Tk")
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def input_manager(tk_root):
    frame = ttk.Frame(tk_root)
    return InputManager(frame, ttk.Entry)


def _fake_entry(title: str):
    return SimpleNamespace(title=title, username="user", url="http://example.com")


def test_clear_entries_empties_all_entry_state(input_manager):
    input_manager.entries = [_fake_entry("a")]
    input_manager.original_entries = [_fake_entry("a"), _fake_entry("b")]
    input_manager.current_entry = _fake_entry("a")

    input_manager.clear_entries()

    assert input_manager.entries == []
    assert input_manager.original_entries == []
    assert input_manager.current_entry is None


def test_filter_publishes_nothing_when_original_entries_empty(input_manager):
    """The guard that prevents ghost suggestions: with no original entries,
    a key release (e.g. BackSpace) must not publish a FILTER event."""
    input_manager.clear_entries()

    published = []
    spy = published.append
    EventBus.subscribe(Events.FILTER, spy)
    try:
        input_manager._handle_filter_input(SimpleNamespace(keysym="BackSpace", char=""))
    finally:
        EventBus.unsubscribe(Events.FILTER, spy)

    assert published == []


def test_status_text_does_not_promise_number_select(tk_root):
    frame = ttk.Frame(tk_root)
    status = StatusDisplay(frame)

    status.show_search_results([_fake_entry("a"), _fake_entry("b"), _fake_entry("c")])

    assert "Press 1-" not in status.label.cget("text")
