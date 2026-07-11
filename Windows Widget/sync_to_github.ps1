# ==============================================================================
# OmniBar - Sync to GitHub Repository
# Target Repo: https://github.com/jDroid-X/Window-Widget
# ==============================================================================

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/jDroid-X/Window-Widget.git"
$WorkDir = Split-Path -Parent $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "         SYNC OMNIBAR TO GITHUB REPOSITORY         " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Target: $RepoUrl" -ForegroundColor Gray
Write-Host ""

Set-Location $WorkDir

# Locate git.exe
$GitCmd = $null
if (Get-Command git -ErrorAction SilentlyContinue) {
    $GitCmd = "git"
} elseif (Test-Path "C:\Program Files\Git\cmd\git.exe") {
    $GitCmd = "C:\Program Files\Git\cmd\git.exe"
} elseif (Test-Path "C:\Program Files (x86)\Git\cmd\git.exe") {
    $GitCmd = "C:\Program Files (x86)\Git\cmd\git.exe"
} elseif (Test-Path "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe") {
    $GitCmd = "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
} else {
    Write-Host "[ERROR] Git was not found in standard paths." -ForegroundColor Red
    Write-Host "Please install Git for Windows from https://git-scm.com/download/win" -ForegroundColor Red
    return
}

Write-Host "[1/4] Initializing Git Repository..." -ForegroundColor Yellow
& $GitCmd init | Out-Null

Write-Host "[2/4] Configuring Remote Origin ($RepoUrl)..." -ForegroundColor Yellow
& $GitCmd remote remove origin 2>$null
& $GitCmd remote add origin $RepoUrl

Write-Host "[3/4] Staging & Committing Files..." -ForegroundColor Yellow
& $GitCmd add .
& $GitCmd commit -m "Update OmniBar: Spectral themes, smart docking, 2-row desktop shortcut, auto-installer" 2>$null

Write-Host "[4/4] Pushing to GitHub (main branch)..." -ForegroundColor Yellow
& $GitCmd branch -M main
& $GitCmd push -u origin main

Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host " Successfully synced to GitHub!" -ForegroundColor Green
Write-Host " https://github.com/jDroid-X/Window-Widget         " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
