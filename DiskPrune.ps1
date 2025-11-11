# PowerShell script for safe disk pruning in E:\projects\atmosphere
# Dry run mode: Lists large/unnecessary files without deleting
# Prune mode: Deletes identified files (use with caution)
# ===================================================

param(
    [switch]$DryRun,
    [long]$MinSizeMB = 100,  # Minimum file size in MB to consider
    [switch]$Backup
)

$targetPath = "E:\projects\atmosphere"
$logFile = "$env:TEMP\DiskPruneLog_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

Add-Content $logFile "Disk Pruning Log - Started: $(Get-Date)"
Add-Content $logFile "Target Path: $targetPath"
Add-Content $logFile "Min Size: $MinSizeMB MB"
Add-Content $logFile "Dry Run: $($DryRun.ToString())"
Add-Content $logFile "`nFiles to Prune:"

# Function to check if file is unnecessary (customize as needed)
function IsUnnecessaryFile($file) {
    $extensionsToPrune = @('.tmp', '.log', '.bak', '.old', '.cache')
    $namesToPrune = @('node_modules', '.git', 'build', 'dist', 'temp', 'cache')
    $ext = [System.IO.Path]::GetExtension($file.FullName).ToLower()
    $name = [System.IO.Path]::GetFileName($file.FullName).ToLower()
    return ($extensionsToPrune -contains $ext) -or ($namesToPrune -contains $name)
}

# Get files
$files = Get-ChildItem -Path $targetPath -File -Recurse -ErrorAction SilentlyContinue | Where-Object {
    ($_.FullName -notlike "*\.git\*") -and ($_.FullName -notlike "*\data\*") -and ($_.Length / 1MB -ge $MinSizeMB -or (IsUnnecessaryFile $_))
}

$backupDir = $null
if ($Backup) {
    $backupDir = "$env:TEMP\DiskPruneBackup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Add-Content $logFile "Backup enabled. Backup directory: $backupDir"
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }
}

$totalSizeMB = 0

foreach ($file in $files) {
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    $totalSizeMB += $sizeMB
    $msg = "$($file.FullName) - Size: $sizeMB MB"
    
    # Backup if enabled
    if ($Backup) {
        $relativePath = $file.FullName.Replace($targetPath, "").TrimStart("\")
        $backupPath = Join-Path $backupDir $relativePath
        $backupParent = Split-Path $backupPath -Parent
        $backupAction = if ($DryRun) { "Would backup" } else { "Backed up" }
        $backupColor = if ($DryRun) { "Yellow" } else { "Green" }
        $backupMsg = "$backupAction $($file.FullName) to $backupPath"
        
        if (-not $DryRun) {
            if (-not (Test-Path $backupParent)) { New-Item -ItemType Directory -Path $backupParent -Force | Out-Null }
            Copy-Item $file.FullName $backupPath -Force
        }
        
        Write-Host $backupMsg -ForegroundColor $backupColor
        Add-Content $logFile $backupMsg
    }
    
    if ($DryRun) {
        Write-Host "Would delete: $msg" -ForegroundColor Yellow
    } else {
        try {
            Remove-Item $file.FullName -Force
            Write-Host "Deleted: $msg" -ForegroundColor Green
        } catch {
            Write-Host "Failed to delete: $msg - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Add-Content $logFile $msg
}

$action = if ($DryRun) { "potentially freed" } else { "freed" }
Add-Content $logFile "`nTotal disk space ${action}: $totalSizeMB MB"
Add-Content $logFile "Operation completed at: $(Get-Date)"

Write-Host "`nDisk pruning completed. Total space ${action}: $totalSizeMB MB" -ForegroundColor Cyan
Write-Host "Log saved at: $logFile" -ForegroundColor Cyan

# Usage:
# Dry run: .\DiskPrune.ps1 -DryRun
# Prune: .\DiskPrune.ps1
