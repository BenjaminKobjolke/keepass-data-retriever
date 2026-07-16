@echo off
echo ========================================
echo  KeePass Data Retriever - Run Tests
echo ========================================
echo.

where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: uv is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo Running tests...
echo.
pushd "%~dp0\.."
uv run pytest tests/ -v --ignore=tests/integration
set TEST_EXIT=%ERRORLEVEL%
popd
if %TEST_EXIT% neq 0 (
    echo.
    echo ========================================
    echo  Some tests failed or no tests collected
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  All tests passed!
    echo ========================================
)
echo.
pause
