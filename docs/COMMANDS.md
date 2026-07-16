# Slash Commands

Slash commands are typed into the search input; press Enter to execute. The input is cleared after every command except `/exit`.

| Command     | Description |
|-------------|-------------|
| `/exit`     | Quit the application. |
| `/reload`   | Reload the KeePass database (prompts for the password if needed). |
| `/settings` | Open the settings window (theme + window frames). |
| `/frame`    | Toggle native OS window frames for all windows (main window, password dialog, settings window). Default: off (frameless). Persisted as `show_frame` in `settings.ini` under `[General]`. The main window updates immediately; dialogs use the new setting the next time they open. Also available as a checkbox in `/settings`. |
