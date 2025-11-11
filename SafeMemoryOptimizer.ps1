# SafeMemoryOptimizer.ps1 - Memory and system optimization script
# Clears temporary files, caches, and optimizes system for better memory usage
# Dry run mode: Simulates actions without performing them
# Optimize mode: Performs optimizations (use with caution)

param(
    [switch]$DryRun
)

$logFile = "$env:TEMP\SafeMemoryOptimizerLog_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

Add-Content $logFile "SafeMemoryOptimizer Log - Started: $(Get-Date)"
Add-Content $logFile "Dry Run: $($DryRun.ToString())"
Add-Content $logFile "`nActions Performed:"

function Clear-TempDirectories {
    $tempPaths = @($env:TEMP, "$env:USERPROFILE\AppData\Local\Temp", "$env:SYSTEMROOT\Temp")
    foreach ($path in $tempPaths) {
        if (Test-Path $path) {
            $files = Get-ChildItem -Path $path -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-1) }
            foreach ($file in $files) {
                $msg = "Clear temp: $($file.FullName)"
                if ($DryRun) {
                    Write-Host "Would $msg" -ForegroundColor Yellow
                } else {
                    try {
                        Remove-Item $file.FullName -Force
                        Write-Host "$msg" -ForegroundColor Green
                    } catch {
                        Write-Host "Failed: $msg - $($_.Exception.Message)" -ForegroundColor Red
                    }
                }
                Add-Content $logFile $msg
            }
        }
    }
}

function Clear-SystemCaches {
    # Clear Windows Update cache (safe)
    $wuCache = "$env:SYSTEMROOT\SoftwareDistribution\Download"
    if (Test-Path $wuCache) {
        $files = Get-ChildItem -Path $wuCache -File -Recurse -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $msg = "Clear Windows Update cache: $($file.FullName)"
            if ($DryRun) {
                Write-Host "Would $msg" -ForegroundColor Yellow
            } else {
                try {
                    Remove-Item $file.FullName -Force
                    Write-Host "$msg" -ForegroundColor Green
                } catch {
                    Write-Host "Failed: $msg - $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            Add-Content $logFile $msg
        }
    }

    # Clear Thumbnail cache (safe)
    $thumbCache = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
    if (Test-Path $thumbCache) {
        $files = Get-ChildItem -Path $thumbCache -File -Filter "*.db" -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*thumb*" }
        foreach ($file in $files) {
            $msg = "Clear thumbnail cache: $($file.FullName)"
            if ($DryRun) {
                Write-Host "Would $msg" -ForegroundColor Yellow
            } else {
                try {
                    Remove-Item $file.FullName -Force
                    Write-Host "$msg" -ForegroundColor Green
                } catch {
                    Write-Host "Failed: $msg - $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            Add-Content $logFile $msg
        }
    }
}

function Optimize-System {
    # Run system file checker (safe diagnostic)
    $msg = "Run System File Checker (sfc /scannow)"
    if ($DryRun) {
        Write-Host "Would $msg" -ForegroundColor Yellow
    } else {
        Write-Host "Running $msg..." -ForegroundColor Cyan
        Start-Process -FilePath "sfc" -ArgumentList "/scannow" -NoNewWindow -Wait
    }
    Add-Content $logFile $msg

    # Empty Recycle Bin (safe)
    $msg = "Empty Recycle Bin"
    if ($DryRun) {
        Write-Host "Would $msg" -ForegroundColor Yellow
    } else {
        Write-Host "Running $msg..." -ForegroundColor Cyan
        Clear-RecycleBin -Force -ErrorAction SilentlyContinue
    }
    Add-Content $logFile $msg
}

# Execute optimizations
Clear-TempDirectories
Clear-SystemCaches
Optimize-System

Add-Content $logFile "`nOptimization completed at: $(Get-Date)"
Write-Host "`nMemory optimization completed." -ForegroundColor Cyan
Write-Host "Log saved at: $logFile" -ForegroundColor Cyan

# Usage:
# Dry run: .\SafeMemoryOptimizer.ps1 -DryRun
# Optimize: .\SafeMemoryOptimizer.ps1
