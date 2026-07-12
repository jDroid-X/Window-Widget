@echo off
:: Uninstall OmniBar Widget

rem Define installation directory
set "TARGET_DIR=%USERPROFILE%\\OmniBar"

rem Stop the installed application before removing its files.
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -like '*\\OmniBar\\main.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

rem Remove desktop shortcut if it exists
set "SHORTCUT=%USERPROFILE%\\Desktop\\jDroid-X OmniBar.lnk"
if exist "%SHORTCUT%" (
    echo Deleting desktop shortcut...
    del "%SHORTCUT%"
)

rem Delete startup registry entry
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "OmniBarWidget" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo Removed startup registry entry.
) else (
    echo No startup registry entry found or already removed.
)

rem Move installation folder to Recycle Bin using PowerShell
powershell -NoProfile -Command "if (Test-Path '%TARGET_DIR%') { $sh = New-Object -ComObject Shell.Application; $fold = $sh.Namespace(0xA); $itm = $fold.ParseName('%TARGET_DIR%'); if ($itm) { $itm.InvokeVerb('delete') } } else { Write-Host 'Installation folder not found; nothing to recycle.' }"

echo Uninstall completed. OmniBar files have been sent to the recycle bin.
pause
