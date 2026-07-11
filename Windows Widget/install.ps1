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
    Write-Host "[ERROR] Python was not found on your system!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/ and ensure 'Add Python to PATH' is checked." -ForegroundColor Red
    return
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
    
    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    
    Write-Host "      Copying files to $TargetDir..." -ForegroundColor Gray
    Copy-Item -Path "$($ExtractedFolder.FullName)\*" -Destination $TargetDir -Recurse -Force
    
    # Clean up temp files
    Remove-Item -Path $TempZip -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-Host "[WARNING] Could not download from GitHub directly (or installing from local directory). Using local files..." -ForegroundColor Yellow
    $ScriptDir = $PSScriptRoot
    if ($ScriptDir -and (Test-Path "$ScriptDir\main.py")) {
        Copy-Item -Path "$ScriptDir\*" -Destination $TargetDir -Recurse -Force
    }
}

# 3. Upgrade pip and install dependencies
Write-Host "[3/5] Installing Python dependencies..." -ForegroundColor Yellow
& $PythonCmd -m pip install --upgrade pip
& $PythonCmd -m pip install -r "$TargetDir\requirements.txt"

# 4. Run installer helper (Desktop shortcut, Startup registry registration)
Write-Host "[4/5] Configuring startup and desktop shortcut..." -ForegroundColor Yellow
& $PythonCmd "$TargetDir\installer_helper.py"

# 5. Launch OmniBar
Write-Host "[5/5] Launching OmniBar Hardware Widget..." -ForegroundColor Green
$PythonwCmd = (Get-Command $PythonCmd).Source -replace "python.exe", "pythonw.exe"
if (-not (Test-Path $PythonwCmd)) {
    $PythonwCmd = $PythonCmd
}

Start-Process -FilePath $PythonwCmd -ArgumentList "`"$TargetDir\main.py`"" -WindowStyle Hidden

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete! OmniBar is now running.   " -ForegroundColor Green
Write-Host "  Desktop Shortcut : jDroid-X OmniBar              " -ForegroundColor Green
Write-Host "  Installed Folder : $TargetDir                    " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
