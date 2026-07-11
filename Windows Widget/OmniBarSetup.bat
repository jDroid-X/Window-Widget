@echo off
cd /d "%~dp0"
title jDroid-X OmniBar Installer Bootstrapper
color 0A
echo ===================================================
echo           jDroid-X OmniBar Setup Bootstrapper
echo ===================================================
echo.

if exist "install.bat" (
    echo Local install.bat detected. Running local installer...
    echo.
    call "install.bat"
    exit /b %errorlevel%
)

if exist "install.ps1" (
    echo Local install.ps1 detected. Running PowerShell installer...
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "install.ps1"
    pause
    exit /b %errorlevel%
)

echo Downloading and running latest installer from GitHub...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $code = Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/jDroid-X/Window-Widget/main/install.ps1' -UseBasicParsing; Invoke-Expression $code"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed or was canceled.
    echo Please ensure you are connected to the Internet and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo You can close this window now.
echo.
pause
exit /b 0
