@echo off
echo ========================================
echo  KeePass Data Retriever - Build Executable
echo ========================================
echo.

where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: uv is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo [1/3] Syncing build dependencies...
uv sync --extra build
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to sync build dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Running PyInstaller...
uv run pyinstaller --name KeepassDataRetriever --onefile --windowed main.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [3/3] Copying settings.ini to dist...
xcopy "settings.ini" "dist\" /Y /I

echo.
echo ========================================
echo  Build complete: dist\KeepassDataRetriever.exe
echo ========================================
echo.
pause
