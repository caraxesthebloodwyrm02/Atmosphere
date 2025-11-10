# Comprehensive Security Audit for Atmosphere
# Run as Administrator

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$logDir = "E:\SecureWorkspace\audit_logs"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "$logDir\security_audit_$timestamp.log"

# Create log directory if it doesn't exist
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-AuditLog {
    param([string]$Message, [string]$Level = "INFO")
    $logEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry
    Write-Host $logEntry -ForegroundColor $(switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    })
}

function Test-UCRConfigurations {
    Write-AuditLog "Checking for UCR configurations..."
    
    $ucrPaths = @(
        "$env:APPDATA\Microsoft\Windows\UCR",
        "$env:LOCALAPPDATA\Microsoft\Windows\UCR",
        "$env:ProgramData\Microsoft\Windows\UCR",
        "$env:ProgramFiles\WindowsApps\*UCR*",
        "$env:ProgramFiles (x86)\WindowsApps\*UCR*"
    )
    
    $found = $false
    foreach ($path in $ucrPaths) {
        if (Test-Path $path) {
            $found = $true
            Write-AuditLog "WARNING: Found potential UCR configuration at: $path" "WARN"
            Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue | 
                Select-Object FullName, LastWriteTime, Length | 
                Format-Table -AutoSize | 
                Out-String -Width 200 | 
                ForEach-Object { Write-AuditLog $_ "WARN" }
        }
    }
    
    if (-not $found) {
        Write-AuditLog "No UCR configurations found in common locations." "SUCCESS"
    }
}

function Test-AtmosphereSecurity {
    Write-AuditLog "Auditing Atmosphere security settings..."
    
    # Check for sensitive files
    $sensitiveFiles = @(
        "*.pem", "*.key", "*.p12", "*.pfx", "*.cer", "*.crt",
        "*password*", "*secret*", "*credential*", "*token*",
        "*.env", ".env*", "config*.json", "*.config", "appsettings.*"
    )
    
    $atmosphereDir = "E:\Projects\Atmosphere"
    if (Test-Path $atmosphereDir) {
        foreach ($pattern in $sensitiveFiles) {
            try {
                $files = Get-ChildItem -Path $atmosphereDir -Filter $pattern -Recurse -ErrorAction SilentlyContinue
                foreach ($file in $files) {
                    Write-AuditLog "Sensitive file found: $($file.FullName)" "WARN"
                    
                    # Check file permissions
                    $acl = Get-Acl -Path $file.FullName -ErrorAction SilentlyContinue
                    if ($acl) {
                        $perms = $acl.Access | Where-Object { $_.FileSystemRights -match "FullControl|Modify|Write" }
                        if ($perms) {
                            Write-AuditLog "  Insecure permissions on sensitive file:" "WARN"
                            $perms | ForEach-Object {
                                Write-AuditLog "    $($_.IdentityReference): $($_.FileSystemRights)" "WARN"
                            }
                        }
                    }
                }
            } catch {
                Write-AuditLog "Error checking for $pattern : $_" "ERROR"
            }
        }
    } else {
        Write-AuditLog "Atmosphere directory not found at $atmosphereDir" "WARN"
    }
}

function Test-NetworkConnections {
    Write-AuditLog "Checking for suspicious network connections..."
    
    try {
        $connections = Get-NetTCPConnection -State Established -ErrorAction Stop | 
            Where-Object { $_.RemoteAddress -ne '127.0.0.1' -and $_.RemoteAddress -ne '::1' }
            
        if ($connections) {
            $connections | ForEach-Object {
                $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                $processName = if ($process) { $process.ProcessName } else { "Unknown" }
                
                Write-AuditLog "Connection: $($_.RemoteAddress):$($_.RemotePort) " +
                              "(PID: $($_.OwningProcess), Process: $processName, State: $($_.State))" "INFO"
            }
        } else {
            Write-AuditLog "No active external network connections found." "SUCCESS"
        }
    } catch {
        Write-AuditLog "Error checking network connections: $_" "ERROR"
    }
}

function Test-EnvironmentVariables {
    Write-AuditLog "Checking environment variables for sensitive data..."
    
    $sensitiveVars = @('PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'CREDENTIAL', 'API_KEY')
    
    Get-ChildItem Env: | ForEach-Object {
        $var = $_
        $sensitive = $sensitiveVars | Where-Object { $var.Name -like "*$_*" }
        
        if ($sensitive) {
            $value = if ($var.Value.Length -gt 20) { 
                $var.Value.Substring(0, 5) + "..." + $var.Value.Substring($var.Value.Length - 5) 
            } else { 
                $var.Value 
            }
            
            Write-AuditLog "Sensitive environment variable found: $($var.Name)=$value" "WARN"
        }
    }
}

function Test-ScheduledTasks {
    Write-AuditLog "Checking for suspicious scheduled tasks..."
    
    try {
        $tasks = Get-ScheduledTask | Where-Object { 
            $_.TaskPath -match "UCR|Atmosphere|Cable|Windsurf" -or
            $_.TaskName -match "UCR|Atmosphere|Cable|Windsurf"
        }
        
        if ($tasks) {
            $tasks | ForEach-Object {
                $task = $_
                $action = $task.Actions | Select-Object -First 1
                
                Write-AuditLog "Scheduled Task: $($task.TaskName)" "INFO"
                Write-AuditLog "  Path: $($task.TaskPath)" "INFO"
                Write-AuditLog "  State: $($task.State)" "INFO"
                
                if ($action) {
                    Write-AuditLog "  Action: $($action.Execute) $($action.Arguments)" "INFO"
                    
                    # Check for suspicious commands
                    $suspicious = @('powershell', 'cmd', 'wscript', 'cscript', 'msbuild', 'mshta')
                    $suspiciousFound = $suspicious | Where-Object { 
                        $action.Execute -match $_ -or $action.Arguments -match $_ 
                    }
                    
                    if ($suspiciousFound) {
                        Write-AuditLog "  WARNING: Suspicious command found in task action!" "WARN"
                    }
                }
                
                # Check task author
                $xml = [xml]($task | Export-ScheduledTask)
                $author = $xml.Task.RegistrationInfo.Author
                if ($author -and $author -notmatch "Microsoft|$env:USERNAME") {
                    Write-AuditLog "  WARNING: Suspicious task author: $author" "WARN"
                }
            }
        } else {
            Write-AuditLog "No suspicious scheduled tasks found." "SUCCESS"
        }
    } catch {
        Write-AuditLog "Error checking scheduled tasks: $_" "ERROR"
    }
}

function Test-Services {
    Write-AuditLog "Checking for suspicious services..."
    
    try {
        $suspiciousServices = Get-Service | Where-Object { 
            $_.DisplayName -match "UCR|Atmosphere|Cable|Windsurf" -or
            $_.Name -match "UCR|Atmosphere|Cable|Windsurf"
        }
        
        if ($suspiciousServices) {
            $suspiciousServices | ForEach-Object {
                $service = $_
                $serviceInfo = Get-WmiObject -Class Win32_Service -Filter "Name='$($service.Name)'"
                
                Write-AuditLog "Service: $($service.DisplayName) ($($service.Name))" "INFO"
                Write-AuditLog "  Status: $($service.Status), StartType: $($service.StartType)" "INFO"
                
                if ($serviceInfo) {
                    Write-AuditLog "  Path: $($serviceInfo.PathName)" "INFO"
                    
                    # Check for unquoted paths with spaces (potential security issue)
                    if ($serviceInfo.PathName -match '^[^"].*\s+.*\.exe') {
                        Write-AuditLog "  WARNING: Unquoted path with spaces detected!" "WARN"
                    }
                    
                    # Check for writable service paths
                    $servicePath = ($serviceInfo.PathName -replace '^"([^"]+)".*', '$1' -replace '^([^\s]+).*', '$1')
                    if (Test-Path $servicePath) {
                        $acl = Get-Acl -Path $servicePath -ErrorAction SilentlyContinue
                        if ($acl) {
                            $writeAccess = $acl.Access | Where-Object { 
                                $_.FileSystemRights -match "Modify|FullControl|Write" -and 
                                $_.IdentityReference -notmatch "SYSTEM|Administrators|CREATOR OWNER"
                            }
                            
                            if ($writeAccess) {
                                Write-AuditLog "  WARNING: Service binary has unexpected write permissions:" "WARN"
                                $writeAccess | ForEach-Object {
                                    Write-AuditLog "    $($_.IdentityReference): $($_.FileSystemRights)" "WARN"
                                }
                            }
                        }
                    }
                }
            }
        } else {
            Write-AuditLog "No suspicious services found." "SUCCESS"
        }
    } catch {
        Write-AuditLog "Error checking services: $_" "ERROR"
    }
}

function Test-StartupPrograms {
    Write-AuditLog "Checking startup programs..."
    
    $startupPaths = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
    )
    
    foreach ($path in $startupPaths) {
        try {
            if ($path.StartsWith("HKCU:") -or $path.StartsWith("HKLM:")) {
                if (Test-Path $path) {
                    Write-AuditLog "Startup entries in $path :" "INFO"
                    Get-ItemProperty -Path $path -ErrorAction SilentlyContinue | 
                        Select-Object -ExpandProperty Property | 
                        ForEach-Object {
                            $value = (Get-ItemProperty -Path $path -Name $_ -ErrorAction SilentlyContinue).$_
                            Write-AuditLog "  $_ = $value" "INFO"
                            
                            # Check for suspicious commands
                            $suspicious = @('powershell', 'cmd', 'wscript', 'cscript', 'msbuild', 'mshta')
                            $suspiciousFound = $suspicious | Where-Object { $value -match $_ }
                            
                            if ($suspiciousFound) {
                                Write-AuditLog "  WARNING: Suspicious command in startup!" "WARN"
                            }
                        }
                }
            } else {
                if (Test-Path $path) {
                    Write-AuditLog "Startup items in $path :" "INFO"
                    Get-ChildItem -Path $path -ErrorAction SilentlyContinue | ForEach-Object {
                        Write-AuditLog "  $($_.Name)" "INFO"
                    }
                }
            }
        } catch {
            Write-AuditLog "Error checking $path : $_" "ERROR"
        }
    }
}

function Test-Processes {
    Write-AuditLog "Checking for suspicious processes..."
    
    try {
        $suspiciousProcesses = Get-Process | Where-Object { 
            $_.ProcessName -match "ucr|atmosphere|cable|windsurf" -or
            $_.MainWindowTitle -match "UCR|Atmosphere|Cable|Windsurf"
        }
        
        if ($suspiciousProcesses) {
            $suspiciousProcesses | ForEach-Object {
                $process = $_
                $processInfo = Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($process.Id)"
                
                Write-AuditLog "Process: $($process.ProcessName) (PID: $($process.Id))" "INFO"
                Write-AuditLog "  Command Line: $($processInfo.CommandLine)" "INFO"
                
                # Check for unsigned executables
                $file = Get-AuthenticodeSignature -FilePath $process.Path -ErrorAction SilentlyContinue
                if ($file -and $file.Status -ne "Valid") {
                    Write-AuditLog "  WARNING: Process is not properly signed or signature is invalid!" "WARN"
                    Write-AuditLog "  Status: $($file.Status), Signer: $($file.SignerCertificate.Subject)" "WARN"
                }
                
                # Check for processes with network connections
                $connections = Get-NetTCPConnection -OwningProcess $process.Id -ErrorAction SilentlyContinue
                if ($connections) {
                    Write-AuditLog "  Network Connections:" "INFO"
                    $connections | ForEach-Object {
                        Write-AuditLog "    $($_.RemoteAddress):$($_.RemotePort) ($($_.State))" "INFO"
                    }
                }
            }
        } else {
            Write-AuditLog "No suspicious processes found." "SUCCESS"
        }
    } catch {
        Write-AuditLog "Error checking processes: $_" "ERROR"
    }
}

# Main execution
Write-Host "=== Atmosphere Security Audit ===" -ForegroundColor Magenta
Write-Host "Starting comprehensive security audit..." -ForegroundColor Cyan
Write-Host "Log file: $logFile" -ForegroundColor Cyan

# Run all security checks
$checks = @(
    @{ Name = "UCR Configurations"; Script = ${function:Test-UCRConfigurations} },
    @{ Name = "Atmosphere Security"; Script = ${function:Test-AtmosphereSecurity} },
    @{ Name = "Network Connections"; Script = ${function:Test-NetworkConnections} },
    @{ Name = "Environment Variables"; Script = ${function:Test-EnvironmentVariables} },
    @{ Name = "Scheduled Tasks"; Script = ${function:Test-ScheduledTasks} },
    @{ Name = "Services"; Script = ${function:Test-Services} },
    @{ Name = "Startup Programs"; Script = ${function:Test-StartupPrograms} },
    @{ Name = "Running Processes"; Script = ${function:Test-Processes} }
)

foreach ($check in $checks) {
    Write-Host "`n=== $($check.Name) ===" -ForegroundColor Yellow
    try {
        & $check.Script
    } catch {
        Write-AuditLog "Error during $($check.Name): $_" "ERROR"
    }
}

Write-Host "`n=== Audit Complete ===" -ForegroundColor Magenta
Write-Host "Review the full report at: $logFile" -ForegroundColor Cyan

# Open the log file
notepad $logFile
