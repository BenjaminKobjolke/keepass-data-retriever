# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KeePass Data Retriever is a Windows desktop application that provides quick KeePass database search via global hotkeys. It uses Python with Tkinter for the GUI and PyKeePass for database access. The application allows users to quickly search their KeePass database and auto-type or paste credentials into other applications.

## Architecture

### Core Components
- `main.py`: Entry point and main KeePassRetriever class that manages database connection and application lifecycle
- `config.py`: Configuration management using INI files with default fallbacks
- `ui/`: UI components
  - `search_window.py`: Main application window coordinator
  - `input/`: Input handling module
    - `input_manager.py`: Manages input fields and keyboard handling for different modes
    - `command_handler.py`: Handles /exit, /reload, /settings commands
  - `password_dialog.py`: Password entry dialog for database unlock
  - `state_manager.py`: Application state management (AppState enum)
  - `keyboard_handler.py`: Handles credential typing/pasting with special character support
  - `entry_actions_handler.py`: Manages actions for selected KeePass entries
  - `action_buttons.py`: Dynamic action buttons that adapt text based on paste_mode setting
  - `mode_indicator.py`: Visual indicator showing current app mode (RECENT/SEARCH/RESULTS/ACTIONS)
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

Project uses `uv` for dependency management. `pyproject.toml` is the single source of truth; `uv.lock` is committed.

### Environment Setup
```bash
# First-time setup: creates .venv/, installs all deps (incl. dev + build extras), runs tests
install.bat

# Update all deps to latest, refresh lock, re-run lint/type/test
update.bat
```

### Running the Application
```bash
# Standard launch
start.bat

# Or directly via uv
uv run python main.py

# With custom database (legacy support)
uv run python main.py --database path/to/database.kdbx

# With password from command line (legacy support)
uv run python main.py --password yourpassword
```

### Tests / Lint / Types
```bash
# Run tests
tools\run_tests.bat
# or: uv run pytest tests/ -v

# Lint
uv run ruff check .

# Type check
uv run mypy .
```

### Building
```bash
# Compile to standalone executable
compile_exe.bat

# Internally: uv sync --extra build && uv run pyinstaller --name KeepassDataRetriever --onefile --windowed main.py
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

The application uses a centralized state system:
- `AppState` enum defines application states (INITIAL, SEARCH, RESULTS_LIST, ENTRY_ACTIONS, HIDDEN)
- `StateManager` handles state transitions and notifies listeners
- Components register as state listeners and update their UI accordingly
- `InputManager` updates the mode indicator based on current state
- `SearchWindow` coordinates all UI components

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