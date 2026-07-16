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
echo [3/4] Copying settings.ini to dist...
xcopy "settings.ini" "dist\" /Y /I

set "DEPLOY_DIR=E:\[--Sync--]\BKTools\Apps\keepass-data-retriever"
echo.
echo [4/4] Deploying to %DEPLOY_DIR%...
if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"
copy /Y "dist\KeepassDataRetriever.exe" "%DEPLOY_DIR%\"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to copy executable to %DEPLOY_DIR%
    pause
    exit /b 1
)
rem Don't clobber existing config on target
if not exist "%DEPLOY_DIR%\settings.ini" copy "settings.ini" "%DEPLOY_DIR%\"

echo.
echo ========================================
echo  Build complete: %DEPLOY_DIR%\KeepassDataRetriever.exe
echo ========================================
echo.
pause
