# Restore Network Configuration
# Run as Administrator to revert IP blocking and restore network settings

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$logFile = "E:\SecureWorkspace\logs\network_restore_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Create logs directory if it doesn't exist
$logDir = Split-Path -Parent $logFile
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $logEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry
    Write-Host $logEntry -ForegroundColor $(switch ($Level) {
        "ERROR" { "Red" }
        "WARN"  { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    })
}

function Remove-BlockedIPRules {
    Write-Log "Removing blocked IP firewall rules..."
    
    try {
        # Get all firewall rules created by our script
        $rules = Get-NetFirewallRule -DisplayName "Block_*_Outbound" -ErrorAction SilentlyContinue
        
        if ($rules) {
            foreach ($rule in $rules) {
                Write-Log "Removing firewall rule: $($rule.DisplayName)"
                Remove-NetFirewallRule -Name $rule.Name -Confirm:$false -ErrorAction Stop
                Write-Log "Successfully removed rule: $($rule.DisplayName)" "SUCCESS"
            }
        } else {
            Write-Log "No blocked IP firewall rules found to remove." "SUCCESS"
        }
    } catch {
        Write-Log "Error removing firewall rules: $_" "ERROR"
    }
}

function Restore-HostsFile {
    Write-Log "Restoring hosts file..."
    
    $hostsPath = "$env:windir\System32\drivers\etc\hosts"
    $hostsBackup = "$hostsPath.bak"
    
    try {
        if (Test-Path $hostsBackup) {
            Write-Log "Restoring hosts file from backup..."
            Copy-Item -Path $hostsBackup -Destination $hostsPath -Force -ErrorAction Stop
            Write-Log "Successfully restored hosts file from backup" "SUCCESS"
        } else {
            # If no backup exists, remove any blocking entries
            $hostsContent = Get-Content -Path $hostsPath -ErrorAction Stop
            $filteredContent = $hostsContent | Where-Object {
                $_ -notmatch "^\s*# Blocked by" -and 
                $_ -notmatch "^\s*0\.0\.0\.0" -and
                $_ -notmatch "^\s*::"
            }
            
            if ($filteredContent -ne $hostsContent) {
                $filteredContent | Set-Content -Path $hostsPath -Force -ErrorAction Stop
                Write-Log "Cleaned up blocking entries from hosts file" "SUCCESS"
            } else {
                Write-Log "No blocking entries found in hosts file" "INFO"
            }
        }
    } catch {
        Write-Log "Error restoring hosts file: $_" "ERROR"
    }
}

function Reset-WindowsFirewall {
    Write-Log "Resetting Windows Firewall to default settings..."
    
    try {
        # Reset firewall to default settings
        netsh advfirewall reset | Out-File -FilePath $logFile -Append
        Write-Log "Successfully reset Windows Firewall to default settings" "SUCCESS"
        
        # Re-enable necessary firewall profiles
        Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True -ErrorAction Stop
        Write-Log "Re-enabled all firewall profiles" "SUCCESS"
        
    } catch {
        Write-Log "Error resetting Windows Firewall: $_" "ERROR"
    }
}

function Restore-NetworkSettings {
    Write-Log "Restoring network settings..."
    
    try {
        # Reset network adapters
        $adapters = Get-NetAdapter -Physical | Where-Object { $_.Status -eq "Up" }
        foreach ($adapter in $adapters) {
            Write-Log "Resetting network adapter: $($adapter.Name)"
            Disable-NetAdapter -Name $adapter.Name -Confirm:$false -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Enable-NetAdapter -Name $adapter.Name -ErrorAction SilentlyContinue
            Write-Log "Successfully reset network adapter: $($adapter.Name)" "SUCCESS"
        }
        
        # Flush DNS cache
        ipconfig /flushdns | Out-Null
        Write-Log "Flushed DNS cache" "SUCCESS"
        
        # Reset TCP/IP stack
        netsh int ip reset | Out-File -FilePath $logFile -Append
        Write-Log "Reset TCP/IP stack" "SUCCESS"
        
        # Reset Winsock
        netsh winsock reset | Out-File -FilePath $logFile -Append
        Write-Log "Reset Winsock" "SUCCESS"
        
    } catch {
        Write-Log "Error restoring network settings: $_" "ERROR"
    }
}

function Restore-StartupPrograms {
    Write-Log "Restoring startup programs..."
    
    try {
        # Re-enable common startup programs that might have been disabled
        $startupItems = @(
            "OneDrive",
            "Microsoft Edge",
            "Google Chrome",
            "Dropbox",
            "iTunes",
            "Spotify",
            "Discord",
            "Steam",
            "EpicGamesLauncher",
            "NVIDIA",
            "Realtek",
            "Logitech",
            "Razer",
            "Corsair",
            "iCUE",
            "Adobe",
            "Microsoft Office"
        )
        
        $startupPaths = @(
            "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
            "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
        )
        
        foreach ($path in $startupPaths) {
            if (Test-Path $path) {
                foreach ($item in $startupItems) {
                    $backupFile = "${path}_bak\${item}.lnk"
                    if (Test-Path $backupFile) {
                        $targetFile = Join-Path -Path $path -ChildPath "${item}.lnk"
                        if (-not (Test-Path $targetFile)) {
                            Copy-Item -Path $backupFile -Destination $targetFile -Force -ErrorAction SilentlyContinue
                            Write-Log "Restored startup item: $item" "SUCCESS"
                        }
                    }
                }
            }
        }
        
    } catch {
        Write-Log "Error restoring startup programs: $_" "ERROR"
    }
}

# Main execution
Write-Host "=== Network Configuration Restore ===" -ForegroundColor Magenta
Write-Host "Starting network restoration process..." -ForegroundColor Cyan
Write-Host "Log file: $logFile" -ForegroundColor Cyan

# Run all restore functions
$restoreSteps = @(
    @{ Name = "Removing Blocked IP Rules"; Script = ${function:Remove-BlockedIPRules} },
    @{ Name = "Restoring Hosts File"; Script = ${function:Restore-HostsFile} },
    @{ Name = "Resetting Windows Firewall"; Script = ${function:Reset-WindowsFirewall} },
    @{ Name = "Restoring Network Settings"; Script = ${function:Restore-NetworkSettings} },
    @{ Name = "Restoring Startup Programs"; Script = ${function:Restore-StartupPrograms} }
)

foreach ($step in $restoreSteps) {
    Write-Host "`n=== $($step.Name) ===" -ForegroundColor Yellow
    try {
        & $step.Script
    } catch {
        Write-Log "Error during $($step.Name): $_" "ERROR"
    }
}

Write-Host "`n=== Restore Complete ===" -ForegroundColor Magenta
Write-Host "Review the full restore log at: $logFile" -ForegroundColor Cyan
Write-Host "A system restart is recommended to complete the restoration process." -ForegroundColor Yellow

# Open the log file
notepad $logFile
