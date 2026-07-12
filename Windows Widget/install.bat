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
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 goto nopython
    set PYCMD=py
) else (
    set PYCMD=python
)

:: 2. Terminate any existing OmniBar processes before reinstalling using Python
echo [1/4] Stopping any running OmniBar instances...
%PYCMD% -c "import psutil, os; [p.terminate() for p in psutil.process_iter(['pid','name','cmdline']) if p.info['pid'] != os.getpid() and p.info.get('cmdline') and 'main.py' in ' '.join(p.info['cmdline']).lower() and 'omnibar' in ' '.join(p.info['cmdline']).lower()]" >nul 2>&1
echo    Done.
echo.

:: 3. Run the installer helper script (copies files, installs deps, registers startup, creates shortcut)
echo [2/4] Running installer helper...
%PYCMD% installer\installer_helper.py
if %errorlevel% neq 0 goto installfailed
echo.

:: 4. Resolve pythonw.exe path dynamically and launch OmniBar
echo [3/4] Launching OmniBar in background...
for /f "tokens=*" %%P in ('%PYCMD% -c "import sys,os; print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"') do set PYTHONW=%%P
if not exist "%PYTHONW%" set PYTHONW=pythonw.exe
start "" /b "%PYTHONW%" "%USERPROFILE%\OmniBar\main.py"
echo.

:: 5. Success
echo [4/4] Installation complete!
echo.
echo ===================================================
echo   OmniBar Hardware Widget is now running!
echo   Installed to: %USERPROFILE%\OmniBar
echo   Desktop shortcut: jDroid-X OmniBar
echo ===================================================
echo.
echo This terminal window will close automatically...
timeout /t 2 >nul
exit

:nopython
echo.
echo [ERROR] Python is not installed or not in your Windows PATH!
echo Please install Python 3.8+ (and check "Add Python to PATH" during setup).
echo Download: https://www.python.org/downloads/
echo.
echo Press any key to close this window...
pause >nul
exit /b 1

:installfailed
echo.
echo [ERROR] Installation failed during helper execution.
echo Check the output above for details.
echo.
echo Press any key to close this window...
pause >nul
exit /b 1
