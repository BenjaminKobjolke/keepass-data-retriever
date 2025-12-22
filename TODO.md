# Refactoring TODO

## Project Overview
KeePass Data Retriever - Windows desktop app for quick KeePass database search via global hotkeys.
Uses Python + Tkinter. Main entry: `main.py`, UI in `ui/` directory.

## Architecture Context
- `ui/search_window.py` - Main coordinator, creates all UI components
- `ui/input/input_manager.py` - Handles search/list/action input modes (uses EventBus)
- `ui/action_buttons.py` - Shows action buttons for selected entry
- `ui/entry_actions_handler.py` - Executes actions (copy, paste, type credentials)
- `ui/results_view.py` - Displays search results list
- `ui/state_manager.py` - Manages AppState transitions (INITIAL, SEARCH, RESULTS_LIST, ENTRY_ACTIONS, HIDDEN)
- `ui/events.py` - EventBus for pub/sub pattern

## Completed Refactoring
- [x] `ui/constants.py` - Contains `Actions`, `Fonts`, `Styles` classes
- [x] `ui/action_registry.py` - Centralized action definitions with `ActionRegistry` class
- [x] `ui/events.py` - `EventBus` class for pub/sub pattern
- [x] `ui/input/input_manager.py` - Uses `ActionRegistry.get_action_by_key()` and EventBus
- [x] `ui/action_buttons.py` - Uses `ActionRegistry.get_all_actions()` and `get_label()`, removed singleton
- [x] `ui/results_view.py` - Uses `Fonts.SMALL`, `Fonts.NORMAL`, `Styles.*` constants
- [x] `ui/input/command_handler.py` - Uses EventBus for /exit, /reload, /settings
- [x] `ui/search_window.py` - Subscribes to EventBus events

---

## Completed Tasks

### Task 1: Fix ActionButtons Singleton ✓
Removed singleton pattern from `ui/action_buttons.py`:
- Removed `_instance` class variable
- Removed `get_instance()` classmethod
- Removed instance checking in `on_state_changed()`
- Updated `ui/entry_actions_handler.py` to use direct instantiation

### Task 2: Use EventBus ✓
Replaced 16 callback parameters with EventBus pattern:
- `InputManager.__init__` now takes only 3 parameters: `parent`, `entry_class`, `state_manager`
- `CommandHandler` uses EventBus for command events
- `SearchWindow` subscribes to all events

---

### UI Improvements ✓
1. **RECENT label fix**: Mode indicator now shows "SEARCH" when no recent entries exist
   - Initial mode is "SEARCH" instead of "RECENT"
   - Only shows "RECENT" when entries are present in data

2. **Results filtering**: Typing in search input filters existing results in real-time
   - Filters by title, username, and URL (case-insensitive)
   - Added `FILTER` event to EventBus
   - Added `original_entries` to store unfiltered results
   - Added `<KeyRelease>` handler for live filtering

---

## Testing Checklist
After changes, verify:
1. [ ] App starts without errors
2. [ ] No recent entries → shows "SEARCH" label
3. [ ] Recent entries exist → shows "RECENT" then "RESULTS"
4. [ ] Search works (type in search box, press Enter)
5. [ ] Results display correctly
6. [ ] Typing filters results in real-time
7. [ ] Clearing filter restores all results
8. [ ] Arrow keys navigate filtered results
9. [ ] Number keys 1-7 trigger actions in action mode
10. [ ] Action buttons appear when entry selected
11. [ ] Mode indicator updates correctly

## Run Command
```bash
cd D:\GIT\BenjaminKobjolke\keepass-data-retriever
python main.py
```
