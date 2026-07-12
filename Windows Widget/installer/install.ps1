# ==============================================================================
# OmniBar Hardware Widget - Automated GitHub Installer (PowerShell)
# Repository: https://github.com/jDroid-X/Window-Widget
# ==============================================================================

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/jDroid-X/Window-Widget"
$ZipUrl = "$RepoUrl/archive/refs/heads/main.zip"
$TargetDir = "$env:USERPROFILE\OmniBar"
$TempZip = "$env:TEMP\OmniBar_main.zip"
$TempExtract = "$env:TEMP\OmniBar_Extract"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "         OMNIBAR HARDWARE WIDGET INSTALLER         " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python installation
Write-Host "[1/5] Checking Python environment..." -ForegroundColor Yellow
$PythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = "py"
} else {
    throw "Python 3.8 or later is required. Install it from https://www.python.org/downloads/ and rerun this installer."
}

# 2. Download and extract latest code from GitHub repository
Write-Host "[2/5] Downloading latest OmniBar release from GitHub ($RepoUrl)..." -ForegroundColor Yellow
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $ZipUrl -OutFile $TempZip -UseBasicParsing
    
    if (Test-Path $TempExtract) {
        Remove-Item -Path $TempExtract -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TempExtract -Force | Out-Null
    
    Write-Host "      Extracting archive..." -ForegroundColor Gray
    Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
    
    # Locate extracted folder (usually Window-Widget-main)
    $ExtractedFolder = Get-ChildItem -Path $TempExtract | Where-Object { $_.PSIsContainer } | Select-Object -First 1
    $SourceFolder = $ExtractedFolder.FullName
    if (Test-Path "$SourceFolder\Windows Widget\Windows Widget\main.py") {
        $SourceFolder = "$SourceFolder\Windows Widget\Windows Widget"
    } elseif (Test-Path "$SourceFolder\Windows Widget\main.py") {
        $SourceFolder = "$SourceFolder\Windows Widget"
    }
    
    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    
    Write-Host "      Copying files from $SourceFolder to $TargetDir..." -ForegroundColor Gray
    Copy-Item -Path "$SourceFolder\*" -Destination $TargetDir -Recurse -Force
    
    # Clean up temp files
    Remove-Item -Path $TempZip -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-Host "[WARNING] GitHub download or extraction failed: $_" -ForegroundColor Yellow
    $ScriptDir = $PSScriptRoot
    $LocalSource = $ScriptDir
    if ($ScriptDir) {
        if (Test-Path "$ScriptDir\Windows Widget\main.py") {
            $LocalSource = "$ScriptDir\Windows Widget"
        } elseif (Test-Path "$ScriptDir\..\main.py") {
            $LocalSource = "$ScriptDir\.."
        }
    }
    if (Test-Path "$LocalSource\main.py") {
        Write-Host "      Copying local files from $LocalSource to $TargetDir..." -ForegroundColor Gray
        Copy-Item -Path "$LocalSource\*" -Destination $TargetDir -Recurse -Force
    } else {
        Write-Host ""
        Write-Host "===================================================" -ForegroundColor Red
        Write-Host "  [FATAL ERROR] Installation Failed!               " -ForegroundColor Red
        Write-Host "  Could not download OmniBar from GitHub, and no    " -ForegroundColor Red
        Write-Host "  local files were found in: $ScriptDir             " -ForegroundColor Red
        Write-Host "===================================================" -ForegroundColor Red
        Write-Host "Please ensure you have an active internet connection," -ForegroundColor Red
        Write-Host "or extract the release ZIP and run install.bat/ps1" -ForegroundColor Red
        Write-Host "directly from the extracted folder." -ForegroundColor Red
        Write-Host ""
        exit 1
    }
}

# 3. Terminate any running OmniBar instances to prevent duplicates
Write-Host "[3/5] Stopping any running OmniBar instances..." -ForegroundColor Yellow
try {
    # Kill pythonw/python processes whose command line contains OmniBar\main.py
    Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -and $_.CommandLine -match 'OmniBar.*main\.py'
    } | ForEach-Object {
        Write-Host "      Terminating PID $($_.ProcessId) ($($_.Name))" -ForegroundColor Gray
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "      (No existing instances found)" -ForegroundColor Gray
}

# 4. Run installer helper (dependencies, shortcut, and startup registration)
Write-Host "[4/5] Configuring OmniBar..." -ForegroundColor Yellow
& $PythonCmd "$TargetDir\installer\installer_helper.py"

# 5. Launch OmniBar (single instance only)
Write-Host "[5/5] Launching OmniBar Hardware Widget..." -ForegroundColor Green
try {
    $PythonwCmd = "pythonw.exe"
    if (Get-Command pythonw -ErrorAction SilentlyContinue) {
        $PythonwCmd = (Get-Command pythonw).Source
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonwCmd = (Get-Command python).Source.ToLower().Replace("python.exe", "pythonw.exe")
    }
    if (-not (Test-Path $PythonwCmd)) {
        $PythonwCmd = "pythonw.exe"
    }
    Start-Process -FilePath $PythonwCmd -ArgumentList "`"$TargetDir\main.py`""
} catch {
    Start-Process -FilePath "pythonw.exe" -ArgumentList "`"$TargetDir\main.py`"" -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete! OmniBar is now running.   " -ForegroundColor Green
Write-Host "  Desktop Shortcut : jDroid-X OmniBar              " -ForegroundColor Green
Write-Host "  Installed Folder : $TargetDir                    " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
