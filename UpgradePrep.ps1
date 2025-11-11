# UpgradePrep.ps1 - Automate pre-upgrade tasks: Uninstall Intel drivers, clean registry, prep for AMD/UEFI
# Run as Administrator

param(
    [switch]$DryRun
)

$logFile = "$env:TEMP\UpgradePrepLog_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

Add-Content $logFile "Upgrade Prep Log - Started: $(Get-Date)"
Add-Content $logFile "Dry Run: $($DryRun.ToString())"

function Uninstall-IntelDrivers {
    Write-Host "Uninstalling Intel Drivers..." -ForegroundColor Cyan
    $intelDevices = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*Intel*" -and $_.Status -eq 'OK' }
    foreach ($device in $intelDevices) {
        $msg = "Uninstalling: $($device.FriendlyName)"
        if ($DryRun) {
            Write-Host "Would $msg" -ForegroundColor Yellow
        } else {
            try {
                & pnputil /delete-driver $device.InstanceId /uninstall /force
                Write-Host "$msg - Success" -ForegroundColor Green
            } catch {
                Write-Host "$msg - Failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        Add-Content $logFile $msg
    }
}

function Remove-IntelSoftware {
    Write-Host "Removing Intel Software..." -ForegroundColor Cyan
    $intelApps = Get-WmiObject -Class Win32_Product | Where-Object { $_.Vendor -like "*Intel*" }
    foreach ($app in $intelApps) {
        $msg = "Uninstalling: $($app.Name)"
        if ($DryRun) {
            Write-Host "Would $msg" -ForegroundColor Yellow
        } else {
            try {
                $app.Uninstall()
                Write-Host "$msg - Success" -ForegroundColor Green
            } catch {
                Write-Host "$msg - Failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        Add-Content $logFile $msg
    }
}

function Disable-IntelServices {
    Write-Host "Disabling Intel Services..." -ForegroundColor Cyan
    $intelServices = Get-Service | Where-Object { $_.DisplayName -like "*Intel*" } | Where-Object { $_.Status -eq 'Running' }
    foreach ($service in $intelServices) {
        $msg = "Disabling: $($service.DisplayName)"
        try {
            Stop-Service $service -Force -ErrorAction Stop
            Set-Service $service -StartupType Disabled -ErrorAction Stop
            Write-Host "$msg - Success" -ForegroundColor Green
        } catch {
            Write-Host "$msg - Skipped: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        Add-Content $logFile $msg
    }
}

function Clean-Registry {
    Write-Host "Cleaning Registry (Intel Keys)..." -ForegroundColor Cyan
    $intelKeys = @(
        "HKLM:\SOFTWARE\Intel",
        "HKLM:\SYSTEM\CurrentControlSet\Services\*Intel*"
    )
    foreach ($key in $intelKeys) {
        $msg = "Removing: $key"
        if ($DryRun) {
            Write-Host "Would $msg" -ForegroundColor Yellow
        } else {
            try {
                Remove-Item -Path $key -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "$msg - Success" -ForegroundColor Green
            } catch {
                Write-Host "$msg - Failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        Add-Content $logFile $msg
    }
}

function Prep-ForUpgrade {
    Write-Host "General Upgrade Prep..." -ForegroundColor Cyan
    # Disable Windows Update temporarily
    $msg = "Disabling Windows Update Service"
    try {
        Stop-Service wuauserv -Force -ErrorAction Stop
        Set-Service wuauserv -StartupType Disabled -ErrorAction Stop
        Write-Host "$msg - Success" -ForegroundColor Green
    } catch {
        Write-Host "$msg - Skipped: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    Add-Content $logFile $msg

    # Create restore point
    $msg = "Creating System Restore Point"
    try {
        Checkpoint-Computer -Description "Pre-Upgrade Backup" -RestorePointType MODIFY_SETTINGS -ErrorAction Stop
        Write-Host "$msg - Success" -ForegroundColor Green
    } catch {
        Write-Host "$msg - Skipped: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    Add-Content $logFile $msg
}

# Execute prep
Uninstall-IntelDrivers
Remove-IntelSoftware
Disable-IntelServices
Clean-Registry
Prep-ForUpgrade

Add-Content $logFile "Upgrade Prep completed at: $(Get-Date)"
Write-Host "`nUpgrade prep completed. Reboot and enter BIOS to enable UEFI/disable legacy." -ForegroundColor Cyan
Write-Host "Log saved at: $logFile" -ForegroundColor Cyan

# Usage:
# Dry run: .\UpgradePrep.ps1 -DryRun
# Full prep: .\UpgradePrep.ps1
