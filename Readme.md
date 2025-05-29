# KeePass Data Retriever

A minimalistic tool to quickly search and retrieve data from KeePass databases.

## Usage

Press the configured hotkey (default: alt+shift+F8) to open a minimalistic input window.

Type the name of the KeePass entry and press enter.

Recent entries for the active window are displayed with a slightly different background color. You can delete these recent entries by highlighting them and pressing the `Del` key.

The username and password of the matching KeePass entry will be copied to the clipboard.
You need a multi-clipboard tool to access the last two entries.

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
    - `search_reset_timeout`: Timeout in seconds before resetting the search window
    - `database_idle_timeout`: Timeout in seconds before locking the database
    - `search_hotkey`: Hotkey combination to open the search window

## Dependencies

-   Python 3.10+
-   PyKeePass
-   Tkinter
-   pynput
-   pyperclip
-   pywin32
-   global-hotkeys
