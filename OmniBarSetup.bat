@echo off
title jDroid-X OmniBar Installer Bootstrapper
color 0A
echo ===================================================
echo           jDroid-X OmniBar Setup Bootstrapper
echo ===================================================
echo.
echo This bootstrapper will download and install OmniBar
echo and any missing requirements (including Python).
echo.
echo Please wait, checking environment and downloading files...
echo.

:: Execute the web installer script from the GitHub repository
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
