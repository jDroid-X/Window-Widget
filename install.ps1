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
    Write-Host "Python not found. Downloading and installing Python automatically..." -ForegroundColor Yellow
    $PythonInstallerPath = "$env:TEMP\python-installer.exe"
    $PythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonInstallerPath -UseBasicParsing
    
    Write-Host "Installing Python quietly (this may take a minute)..." -ForegroundColor Yellow
    Start-Process -FilePath $PythonInstallerPath -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1" -Wait
    
    # Clean installer
    Remove-Item $PythonInstallerPath -Force -ErrorAction SilentlyContinue
    
    # Reload environment variables for this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonCmd = "python"
        Write-Host "Python installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Auto-installation of Python failed. Please download Python manually from https://www.python.org/downloads/" -ForegroundColor Red
        return
    }
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
    if (Test-Path "$SourceFolder\Windows Widget\main.py") {
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
try {
    $PythonwCmd = "pythonw"
    if (Get-Command pythonw -ErrorAction SilentlyContinue) {
        $PythonwCmd = (Get-Command pythonw).Source
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonwCmd = (Get-Command python).Source -replace "python.exe", "pythonw.exe"
    }
    if (-not (Test-Path $PythonwCmd)) {
        $PythonwCmd = "pythonw"
    }
    Start-Process -FilePath $PythonwCmd -ArgumentList "`"$TargetDir\main.py`"" -WindowStyle Hidden
} catch {
    Start-Process -FilePath "pythonw.exe" -ArgumentList "`"$TargetDir\main.py`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete! OmniBar is now running.   " -ForegroundColor Green
Write-Host "  Desktop Shortcut : jDroid-X OmniBar              " -ForegroundColor Green
Write-Host "  Installed Folder : $TargetDir                    " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
