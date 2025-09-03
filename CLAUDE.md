# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KeePass Data Retriever is a Windows desktop application that provides quick KeePass database search via global hotkeys. It uses Python with Tkinter for the GUI and PyKeePass for database access. The application allows users to quickly search their KeePass database and auto-type or paste credentials into other applications.

## Architecture

### Core Components
- `main.py`: Entry point and main KeePassRetriever class that manages database connection and application lifecycle
- `config.py`: Configuration management using INI files with default fallbacks
- `ui/`: UI components organized in a modular view-based architecture
  - `search_window.py`: Main application window using ViewManager for orchestration
  - `base_view.py`: Abstract base class for all views
  - `view_manager.py`: Centralized view controller that manages view transitions
  - `views/`: Modular view implementations
    - `initial_view.py`: Welcome state with recent entries
    - `search_view.py`: Active search input with live results
    - `results_list_view.py`: Multiple search results navigation
    - `entry_details_view.py`: Selected entry with action buttons
  - `password_dialog.py`: Password entry dialog for database unlock
  - `state_manager.py`: Application state management (AppState enum)
  - `keyboard_handler.py`: Handles credential typing/pasting with special character support
  - `entry_actions_handler.py`: Manages actions for selected KeePass entries
  - `action_buttons.py`: Dynamic action buttons that adapt text based on paste_mode setting
  - Window management: `window_manager.py`, `window_relations_manager.py`
  - UI components: `results_view.py`, `status_display.py`, `dark_entry.py`

### Key Features
- Global hotkey activation (default: alt+shift+F8)
- Recent entries tracking per window with deletion capability (Del key)
- Paste mode for reliable credential insertion (handles special characters like ^)
- Auto-type functionality for username/password combinations
- Multi-clipboard support for username/password copying
- Auto-lock database after idle timeout
- Window positioning modes (mouse, center, center_screen)

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
install.bat

# Manual activation for development
activate_environment.bat
```

### Running the Application
```bash
# Run directly with Python
python main.py

# Run with custom database (legacy support)
python main.py --database path/to/database.kdbx

# Run with password from command line (legacy support)  
python main.py --password yourpassword
```

### Building
```bash
# Compile to standalone executable
compile_exe.bat

# This runs: pyinstaller --name KeepassDataRetriever --onefile --windowed main.py
# Output: dist/KeepassDataRetriever.exe
```

## Configuration

The application uses `settings.ini` for configuration. Copy `settings_example.ini` to `settings.ini` and modify:

```ini
[General]
database_path = C:/path/to/database.kdbx
search_reset_timeout = 180
database_idle_timeout = 3600
debug_mode = false
window_position = mouse
paste_mode = true  # Use Ctrl+V paste instead of character typing

[Hotkeys]
search_hotkey = alt + shift + F8
```

### Important Configuration Notes
- `paste_mode`: Controls how credentials are inserted
  - `true` (default): Uses clipboard paste (Ctrl+V) - more reliable with special characters
  - `false`: Types character by character - automatically uses paste for passwords with `^` to avoid dead key issues
- The GUI dynamically updates button labels based on paste_mode ("Paste username" vs "Type username")

## Database Management

- Database connection is managed in `main.py:KeePassRetriever`
- Password authentication via GUI dialog (`ui/password_dialog.py`)
- Auto-lock after idle timeout to protect sensitive data
- Window relations stored in `window-relations.json` for recent entries tracking

## UI State Management

The application uses a centralized state system with modular views:
- `AppState` enum defines application states (INITIAL, SEARCH, RESULTS_LIST, ENTRY_ACTIONS, etc.)
- `StateManager` handles state transitions and notifies listeners
- `ViewManager` orchestrates view transitions based on state changes
- Each view in `ui/views/` handles its own UI logic and responds to specific states
- Views communicate through callbacks rather than direct coupling

### View Architecture
Each view extends `BaseView` and implements:
- `get_supported_states()`: States this view can handle
- `create_ui()`: UI element creation
- `on_show(data)`: Called when view becomes active
- `on_hide()`: Called when view is hidden
- State-specific event handlers for user interaction

This modular approach makes it easy to:
- Add new views without modifying existing code
- Test views in isolation
- Maintain clear separation of concerns
- Extend functionality through composition

## Keyboard Handler and Special Characters

The `KeyboardHandler` class in `ui/keyboard_handler.py` manages credential typing/pasting:
- Respects the `paste_mode` configuration setting
- Automatically detects passwords with problematic characters (like `^`) and uses paste mode
- Dead key handling: The `^` character is a dead key on many keyboard layouts that causes issues with character-by-character typing
- Solution: Use clipboard paste (Ctrl+V) which bypasses keyboard layout issues

## Testing

No formal test framework is configured. Manual testing is done using the provided `test.kdbx` database.

### Testing Credential Input
To test special character handling:
1. Create test entries with passwords containing `^`, `@`, `!`, etc.
2. Test with `paste_mode=true` and `paste_mode=false` in settings.ini
3. Verify that passwords with `^` always use paste mode to avoid dead key issues