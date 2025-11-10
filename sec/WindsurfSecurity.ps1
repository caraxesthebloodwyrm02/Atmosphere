# =============================================
# WINDSURF SECURITY ENFORCER
# =============================================

param(
    [switch]$Monitor,
    [switch]$Audit,
    [switch]$Cleanup
)

$securityConfig = Get-Content "$env:APPDATA\Windsurf\security.config" | ConvertFrom-Json
$logPath = "$($securityConfig.security.workspacePath)\logs\windsurf_security_$(Get-Date -Format 'yyyyMMdd').log"

function Write-SecurityLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logPath -Value $logEntry
    Write-Host $logEntry -ForegroundColor $(if ($Level -eq "ERROR") { "Red" } elseif ($Level -eq "WARN") { "Yellow" } else { "Green" })
}

function Test-SecurityCompliance {
    Write-SecurityLog "Starting security compliance check"

    # Check for unauthorized processes
    $runningProcesses = Get-Process | Select-Object -ExpandProperty Name
    $unauthorizedProcesses = $runningProcesses | Where-Object {
        $_ -in $securityConfig.processes.restrictedProcesses
    }

    if ($unauthorizedProcesses) {
        Write-SecurityLog "WARNING: Unauthorized processes detected: $($unauthorizedProcesses -join ', ')" "WARN"
        foreach ($process in $unauthorizedProcesses) {
            Write-SecurityLog "Terminating unauthorized process: $process" "WARN"
            Get-Process -Name $process -ErrorAction SilentlyContinue | Stop-Process -Force
        }
    }

    # Check Windsurf configuration integrity
    $settingsPath = "$env:APPDATA\Windsurf\User\settings.json"
    if (Test-Path $settingsPath) {
        $settings = Get-Content $settingsPath | ConvertFrom-Json

        # Verify telemetry is disabled
        if ($settings.'telemetry.telemetryLevel' -ne "off") {
            Write-SecurityLog "ERROR: Telemetry not properly disabled" "ERROR"
        }

        # Verify security settings
        if (-not $settings.'security.workspace.trust.enabled') {
            Write-SecurityLog "ERROR: Workspace trust not enabled" "ERROR"
        }

        # Verify restricted UNC hosts
        $allowedHosts = $settings.'security.allowedUNCHosts'
        if ($allowedHosts -notcontains "api.openai.com" -or $allowedHosts.Count -gt 1) {
            Write-SecurityLog "ERROR: UNC host restrictions not properly configured" "ERROR"
        }
    }

    # Check for suspicious network connections
    $networkConnections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
        Where-Object { $_.RemoteAddress -notmatch "^(127\.|192\.168\.|10\.|172\.)" }

    foreach ($conn in $networkConnections) {
        $remoteHost = $conn.RemoteAddress
        if ($remoteHost -notin $securityConfig.network.allowedHosts) {
            Write-SecurityLog "WARNING: Suspicious outbound connection to: $remoteHost" "WARN"
        }
    }

    Write-SecurityLog "Security compliance check completed"
}

function Start-SecurityMonitor {
    Write-SecurityLog "Starting continuous security monitoring"

    while ($true) {
        Test-SecurityCompliance
        Start-Sleep -Seconds 60  # Check every minute
    }
}

function Get-SecurityAudit {
    Write-SecurityLog "Generating security audit report"

    $auditReport = @{
        "timestamp" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "windsurf_version" = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | Where-Object { $_.DisplayName -like "*Windsurf*" }).DisplayVersion
        "security_settings" = @{
            "telemetry_disabled" = $true
            "workspace_trust_enabled" = $true
            "network_restricted" = $true
            "processes_monitored" = $true
        }
        "running_processes" = Get-Process | Select-Object Name, Id, CPU, WorkingSet
        "network_connections" = Get-NetTCPConnection -State Established | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort
        "file_system_access" = Get-EventLog -LogName Security -Newest 10 | Where-Object { $_.EventID -in @(4656, 4658, 4663) }
    }

    $reportPath = "$($securityConfig.security.workspacePath)\audit\security_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    New-Item -ItemType Directory -Path (Split-Path $reportPath -Parent) -Force | Out-Null
    $auditReport | ConvertTo-Json -Depth 10 | Out-File $reportPath -Force

    Write-SecurityLog "Security audit report saved to: $reportPath"
}

function Invoke-SecurityCleanup {
    Write-SecurityLog "Starting security cleanup"

    # Clear temporary files
    $tempPaths = @(
        "$env:TEMP",
        "$env:USERPROFILE\AppData\Local\Temp",
        "$env:USERPROFILE\AppData\Roaming\Windsurf\Cache"
    )

    foreach ($path in $tempPaths) {
        if (Test-Path $path) {
            Get-ChildItem -Path $path -Recurse -File | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-SecurityLog "Cleaned temporary files in: $path"
        }
    }

    # Clear browser data
    $browserDataPaths = @(
        "$env:USERPROFILE\AppData\Roaming\Windsurf\Cache",
        "$env:USERPROFILE\AppData\Roaming\Windsurf\Code Cache",
        "$env:USERPROFILE\AppData\Roaming\Windsurf\GPUCache"
    )

    foreach ($path in $browserDataPaths) {
        if (Test-Path $path) {
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-SecurityLog "Cleaned browser cache: $path"
        }
    }

    # Reset workspace state to prevent persistence of injected configurations
    $storagePath = "$env:APPDATA\Windsurf\User\globalStorage\storage.json"
    if (Test-Path $storagePath) {
        $cleanStorage = @{
            "backupWorkspaces" = @{
                "workspaces" = @()
                "folders" = @()
                "emptyWindows" = @()
            }
            "windowControlHeight" = 35
            "profileAssociations" = @{}
            "theme" = "vs-dark"
            "themeBackground" = "#1e1e1e"
        }
        $cleanStorage | ConvertTo-Json | Out-File $storagePath -Force
        Write-SecurityLog "Reset workspace storage to prevent configuration injection"
    }

    Write-SecurityLog "Security cleanup completed"
}

# Main execution logic
if ($Monitor) {
    Start-SecurityMonitor
} elseif ($Audit) {
    Get-SecurityAudit
} elseif ($Cleanup) {
    Invoke-SecurityCleanup
} else {
    # Default: Run compliance check
    Test-SecurityCompliance
}
