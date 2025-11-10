# Add the automation modules directory to the PSModulePath
$modulePath = "$PWD\automation\modules"
$env:PSModulePath = "$modulePath;$($env:PSModulePath)"

# Verify the modules can be found
Write-Host "=== Module Paths ===" -ForegroundColor Cyan
$env:PSModulePath -split ';' | Where-Object { $_ } | ForEach-Object { Write-Host "- $_" }

# Import the Core module first
$coreModule = "$modulePath\Core\Atmosphere.psm1"
if (Test-Path $coreModule) {
    Write-Host "`nImporting Core module..." -ForegroundColor Cyan
    Import-Module $coreModule -Force -ErrorAction Stop
    Write-Host "Core module imported successfully" -ForegroundColor Green
} else {
    Write-Error "Core module not found at: $coreModule"
    exit 1
}

# Import the Audio module
$audioModule = "$modulePath\Audio\Atmosphere.Audio.psm1"
if (Test-Path $audioModule) {
    Write-Host "`nImporting Audio module..." -ForegroundColor Cyan
    Import-Module $audioModule -Force -ErrorAction Stop
    Write-Host "Audio module imported successfully" -ForegroundColor Green
    
    # List available commands
    Write-Host "`nAvailable Audio commands:" -ForegroundColor Cyan
    Get-Command -Module Atmosphere.Audio | Format-Table -AutoSize
} else {
    Write-Error "Audio module not found at: $audioModule"
    exit 1
}

Write-Host "`nSetup complete! You can now use the Audio module commands." -ForegroundColor Green
