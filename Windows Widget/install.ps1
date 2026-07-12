# ==============================================================================
# OmniBar Hardware Widget - Root Installer Launcher (PowerShell)
# Delegates all work to the installer/install.ps1 script.
# ==============================================================================

# Invoke the actual installer script located in the installer subdirectory
& "$PSScriptRoot\installer\install.ps1"
exit $LASTEXITCODE
