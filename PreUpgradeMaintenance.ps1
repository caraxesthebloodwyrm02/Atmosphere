# PreUpgradeMaintenance.ps1 - Unified pre-upgrade maintenance script
# Combines DiskPrune.ps1 and SafeMemoryOptimizer.ps1 for disk and memory optimization
# Dry run mode: Simulates all actions without performing deletions or changes
# Maintenance mode: Performs optimizations (use with caution)

param(
    [switch]$DryRun,
    [switch]$Backup
)

$logFile = "$env:TEMP\PreUpgradeMaintenanceLog_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

Add-Content $logFile "Pre-Upgrade Maintenance Log - Started: $(Get-Date)"
Add-Content $logFile "Dry Run: $($DryRun.ToString())"
Add-Content $logFile "Backup: $($Backup.ToString())"
Add-Content $logFile "`n=== Cleaning Old Backups ==="

# Function to clean old backups
function Clean-OldBackups {
    param([int]$RetentionDays = 30)
    
    $oldBackups = Get-ChildItem -Path $env:TEMP -Directory -Filter "DiskPruneBackup_*" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-$RetentionDays) }
    
    foreach ($backup in $oldBackups) {
        $msg = "Removing old backup: $($backup.FullName)"
        if ($DryRun) {
            Write-Host "Would $msg" -ForegroundColor Yellow
        } else {
            try {
                Remove-Item $backup.FullName -Recurse -Force
                Write-Host $msg -ForegroundColor Green
            } catch {
                Write-Host "Failed to remove: $msg - $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        Add-Content $logFile $msg
    }
}

# Clean old backups
Clean-OldBackups

Add-Content $logFile "`n=== Disk Pruning Phase ==="

# Run DiskPrune.ps1
$diskPruneParams = @{}
if ($DryRun) { $diskPruneParams.DryRun = $true }
if ($Backup) { $diskPruneParams.Backup = $true }
& .\DiskPrune.ps1 @diskPruneParams

Add-Content $logFile "`n=== Memory Optimization Phase ==="

# Run SafeMemoryOptimizer.ps1
if ($DryRun) {
    & .\SafeMemoryOptimizer.ps1 -DryRun
} else {
    & .\SafeMemoryOptimizer.ps1
}

Add-Content $logFile "`nPre-upgrade maintenance completed at: $(Get-Date)"
Write-Host "`nPre-upgrade maintenance completed." -ForegroundColor Cyan
Write-Host "Combined log saved at: $logFile" -ForegroundColor Cyan

# Usage:
# Dry run: .\PreUpgradeMaintenance.ps1 -DryRun
# Full maintenance: .\PreUpgradeMaintenance.ps1
