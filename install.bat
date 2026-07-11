@echo off
cd /d "%~dp0"
title OmniBar Windows Widget Installer
color 0B
echo ===================================================
echo           OMNIBAR HARDWARE WIDGET INSTALLER        
echo ===================================================
echo.
echo Current Directory: %CD%
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 goto nopython

:: 2. Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

:: 3. Run the installer helper script
python installer_helper.py
if %errorlevel% neq 0 goto installfailed

:: 4. Resolve pythonw.exe path dynamically and launch OmniBar
echo.
echo Launching OmniBar in background...
for /f "tokens=*" %%P in ('python -c "import sys,os; print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"') do set PYTHONW=%%P
if not exist "%PYTHONW%" set PYTHONW=pythonw.exe
start /b "" "%PYTHONW%" "%USERPROFILE%\OmniBar\main.py"
echo.
echo Done! You can close this installer window.
echo.
pause
exit /b 0

:nopython
echo [ERROR] Python is not installed or not in your Windows PATH!
echo Please install Python (and check "Add Python to PATH" during setup).
echo.
pause
exit /b 1

:installfailed
echo [ERROR] Installation failed during helper execution.
echo.
pause
exit /b 1
