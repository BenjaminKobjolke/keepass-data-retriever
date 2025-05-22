@echo off
call activate_environment.bat
call pyinstaller --name KeepassDataRetriever --onefile --windowed main.py
call xcopy "settings.ini" "dist\" /Y /I
