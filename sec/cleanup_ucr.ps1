# UCR Configuration Cleanup Script
# Run as Administrator to remove UCR-related configurations

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$logFile = "E:\SecureWorkspace\logs\ucr_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

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

function Remove-UCRFiles {
    Write-Log "Removing UCR-related files and directories..."
    
    $ucrPaths = @(
        "$env:APPDATA\Microsoft\Windows\UCR",
        "$env:LOCALAPPDATA\Microsoft\Windows\UCR",
        "$env:ProgramData\Microsoft\Windows\UCR",
        "$env:ProgramFiles\WindowsApps\*UCR*",
        "$env:ProgramFiles (x86)\WindowsApps\*UCR*",
        "$env:USERPROFILE\.ucr",
        "$env:USERPROFILE\AppData\Local\UCR",
        "$env:USERPROFILE\AppData\Local\Temp\UCR"
    )
    
    foreach ($path in $ucrPaths) {
        try {
            if (Test-Path $path) {
                Write-Log "Removing: $path"
                Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
                Write-Log "Successfully removed: $path" "SUCCESS"
            }
        } catch {
            Write-Log "Failed to remove $path : $_" "ERROR"
        }
    }
}

function Remove-UCRRegistryKeys {
    Write-Log "Removing UCR registry keys..."
    
    $regPaths = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
    )
    
    foreach ($regPath in $regPaths) {
        try {
            if (Test-Path $regPath) {
                $items = Get-Item -Path $regPath -ErrorAction Stop
                $items.Property | Where-Object { $_ -match "UCR" } | ForEach-Object {
                    Write-Log "Removing registry value: $regPath\$_"
                    Remove-ItemProperty -Path $regPath -Name $_ -Force -ErrorAction Stop
                    Write-Log "Successfully removed registry value: $regPath\$_" "SUCCESS"
                }
            }
        } catch {
            Write-Log "Error processing $regPath : $_" "ERROR"
        }
    }
    
    # Remove UCR-specific registry keys
    $ucrRegPaths = @(
        "HKCU:\Software\UCR",
        "HKLM:\SOFTWARE\UCR",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\UCR",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\UCR"
    )
    
    foreach ($ucrRegPath in $ucrRegPaths) {
        try {
            if (Test-Path $ucrRegPath) {
                Write-Log "Removing registry key: $ucrRegPath"
                Remove-Item -Path $ucrRegPath -Recurse -Force -ErrorAction Stop
                Write-Log "Successfully removed registry key: $ucrRegPath" "SUCCESS"
            }
        } catch {
            Write-Log "Failed to remove $ucrRegPath : $_" "ERROR"
        }
    }
}

function Remove-UCRTasks {
    Write-Log "Removing UCR scheduled tasks..."
    
    try {
        $tasks = Get-ScheduledTask | Where-Object { 
            $_.TaskName -match "UCR" -or 
            $_.TaskPath -match "UCR" -or
            $_.Description -match "UCR"
        }
        
        if ($tasks) {
            foreach ($task in $tasks) {
                Write-Log "Removing scheduled task: $($task.TaskName)"
                $task | Unregister-ScheduledTask -Confirm:$false -ErrorAction Stop
                Write-Log "Successfully removed task: $($task.TaskName)" "SUCCESS"
            }
        } else {
            Write-Log "No UCR-related scheduled tasks found." "SUCCESS"
        }
    } catch {
        Write-Log "Error removing scheduled tasks: $_" "ERROR"
    }
}

function Remove-UCRServices {
    Write-Log "Removing UCR services..."
    
    try {
        $services = Get-Service | Where-Object { 
            $_.Name -match "UCR" -or 
            $_.DisplayName -match "UCR"
        }
        
        if ($services) {
            foreach ($service in $services) {
                Write-Log "Stopping service: $($service.DisplayName)"
                
                # Stop the service if it's running
                if ($service.Status -eq "Running") {
                    Stop-Service -InputObject $service -Force -ErrorAction Stop
                    Write-Log "Stopped service: $($service.DisplayName)" "SUCCESS"
                }
                
                # Disable the service
                Set-Service -Name $service.Name -StartupType Disabled -ErrorAction Stop
                
                # Remove the service
                $serviceInfo = Get-WmiObject -Class Win32_Service -Filter "Name='$($service.Name)'"
                if ($serviceInfo) {
                    $serviceInfo.Delete() | Out-Null
                    Write-Log "Removed service: $($service.DisplayName)" "SUCCESS"
                }
            }
        } else {
            Write-Log "No UCR-related services found." "SUCCESS"
        }
    } catch {
        Write-Log "Error removing services: $_" "ERROR"
    }
}

function Clean-StartupItems {
    Write-Log "Cleaning up startup items..."
    
    $startupPaths = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    
    foreach ($path in $startupPaths) {
        try {
            if (Test-Path $path) {
                Get-ChildItem -Path $path -Filter "*UCR*" -ErrorAction Stop | ForEach-Object {
                    Write-Log "Removing startup item: $($_.FullName)"
                    Remove-Item -Path $_.FullName -Force -ErrorAction Stop
                    Write-Log "Successfully removed: $($_.FullName)" "SUCCESS"
                }
            }
        } catch {
            Write-Log "Error cleaning startup items in $path : $_" "ERROR"
        }
    }
}

function Reset-Permissions {
    Write-Log "Resetting permissions on sensitive directories..."
    
    $directories = @(
        "$env:ProgramData",
        "$env:APPDATA",
        "$env:LOCALAPPDATA",
        "$env:ProgramFiles",
        "$env:ProgramFiles (x86)",
        "$env:USERPROFILE"
    )
    
    foreach ($dir in $directories) {
        try {
            if (Test-Path $dir) {
                Write-Log "Resetting permissions for: $dir"
                $acl = Get-Acl -Path $dir
                $acl.SetAccessRuleProtection($true, $false)
                
                # Add administrators full control
                $adminRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                    "BUILTIN\Administrators",
                    "FullControl",
                    "ContainerInherit,ObjectInherit",
                    "None",
                    "Allow"
                )
                $acl.AddAccessRule($adminRule)
                
                # Add system full control
                $systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                    "NT AUTHORITY\SYSTEM",
                    "FullControl",
                    "ContainerInherit,ObjectInherit",
                    "None",
                    "Allow"
                )
                $acl.AddAccessRule($systemRule)
                
                # Apply the new ACL
                Set-Acl -Path $dir -AclObject $acl -ErrorAction Stop
                Write-Log "Successfully reset permissions for: $dir" "SUCCESS"
            }
        } catch {
            Write-Log "Error resetting permissions for $dir : $_" "ERROR"
        }
    }
}

function Clear-TempFiles {
    Write-Log "Cleaning up temporary files..."
    
    $tempDirs = @(
        $env:TEMP,
        "$env:WINDIR\Temp",
        "$env:LOCALAPPDATA\Temp"
    )
    
    foreach ($tempDir in $tempDirs) {
        try {
            if (Test-Path $tempDir) {
                Write-Log "Cleaning: $tempDir"
                Get-ChildItem -Path $tempDir -Filter "*UCR*" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                
                # Clean up old temporary files
                Get-ChildItem -Path $tempDir -File -Recurse -ErrorAction SilentlyContinue | 
                    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | 
                    Remove-Item -Force -ErrorAction SilentlyContinue
                    
                Write-Log "Successfully cleaned: $tempDir" "SUCCESS"
            }
        } catch {
            Write-Log "Error cleaning $tempDir : $_" "ERROR"
        }
    }
}

# Main execution
Write-Host "=== UCR Configuration Cleanup ===" -ForegroundColor Magenta
Write-Host "Starting UCR cleanup process..." -ForegroundColor Cyan
Write-Host "Log file: $logFile" -ForegroundColor Cyan

# Run all cleanup functions
$cleanupSteps = @(
    @{ Name = "Removing UCR Files"; Script = ${function:Remove-UCRFiles} },
    @{ Name = "Removing UCR Registry Keys"; Script = ${function:Remove-UCRRegistryKeys} },
    @{ Name = "Removing UCR Scheduled Tasks"; Script = ${function:Remove-UCRTasks} },
    @{ Name = "Removing UCR Services"; Script = ${function:Remove-UCRServices} },
    @{ Name = "Cleaning Startup Items"; Script = ${function:Clean-StartupItems} },
    @{ Name = "Resetting Permissions"; Script = ${function:Reset-Permissions} },
    @{ Name = "Cleaning Temporary Files"; Script = ${function:Clear-TempFiles} }
)

foreach ($step in $cleanupSteps) {
    Write-Host "`n=== $($step.Name) ===" -ForegroundColor Yellow
    try {
        & $step.Script
    } catch {
        Write-Log "Error during $($step.Name): $_" "ERROR"
    }
}

Write-Host "`n=== Cleanup Complete ===" -ForegroundColor Magenta
Write-Host "Review the full cleanup log at: $logFile" -ForegroundColor Cyan
Write-Host "A system restart is recommended to complete the cleanup process." -ForegroundColor Yellow

# Open the log file
notepad $logFile
