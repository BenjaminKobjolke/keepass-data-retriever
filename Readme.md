# KeePass Data Retriever

A minimalistic tool to quickly search and retrieve data from KeePass databases.

## Usage

Press the configured hotkey (default: alt+shift+F8) to open a minimalistic input window.

Type the name of the KeePass entry and press enter.

Recent entries for the active window are displayed with a slightly different background color. You can delete these recent entries by highlighting them and pressing the `Del` key.

The username and password of the matching KeePass entry will be copied to the clipboard.
You need a multi-clipboard tool to access the last two entries.

### Special Commands

- **`/exit`**: Exit the application
- **`/reload`**: Reload the KeePass database from disk (useful after making changes in KeePass)

## Configuration

1. Copy `settings_example.ini` to `settings.ini`:

    ```
    cp settings_example.ini settings.ini
    ```

2. Edit `settings.ini` and set your database path:

    ```ini
    [General]
    # For Windows paths, either use double backslashes:
    database_path = C:\\path\\to\\your\\database.kdbx

    # Or use forward slashes (also works on Windows):
    database_path = C:/path/to/your/database.kdbx
    ```

3. Customize other settings as needed:
    - `search_reset_timeout`: Timeout in seconds before resetting the search window (default: 180)
    - `database_idle_timeout`: Timeout in seconds before locking the database (default: 3600)
    - `search_hotkey`: Hotkey combination to open the search window (default: alt+shift+F8)
    - `window_position`: Window positioning mode - 'mouse', 'center', or 'center_screen' (default: mouse)
    - `paste_mode`: Use clipboard paste (Ctrl+V) instead of typing (default: true)
        - When `true`: Credentials are pasted using Ctrl+V (more reliable with special characters)
        - When `false`: Credentials are typed character by character (automatically uses paste for passwords containing `^` to avoid dead key issues)

## Installation

Prerequisite: [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager).

1. Clone the repo.
2. Run `install.bat` — creates `.venv/`, installs all dependencies (including PyInstaller for building), runs tests.
3. Copy `settings_example.ini` to `settings.ini` and configure (see Configuration section above).
4. Launch with `start.bat` (or `uv run python main.py`).

### Update Dependencies

Run `update.bat` to upgrade all packages, refresh `uv.lock`, and re-run lint/type/test checks.

### Build Executable

Run `compile_exe.bat` — produces `dist/KeepassDataRetriever.exe`.

## Dependencies

-   Python 3.11–3.12
-   pykeepass
-   Tkinter (stdlib)
-   pynput
-   pyperclip
-   pyautogui
-   pywin32
-   winhotkeys (custom — pinned git commit)
