# Fix PowerShell Profile Issues

# 1. Create logs directory if it doesn't exist
$logDir = "E:\SecureWorkspace\logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    Write-Host "Created log directory: $logDir" -ForegroundColor Green
}

# 2. Fix read-only alias issue
function Reset-Aliases {
    # Remove conflicting read-only aliases
    $aliasesToRemove = @('rp', 'ep')
    
    foreach ($alias in $aliasesToRemove) {
        if (Get-Alias -Name $alias -ErrorAction SilentlyContinue) {
            Remove-Item -Path "Alias:$alias" -Force -ErrorAction SilentlyContinue
            Write-Host "Removed alias: $alias" -ForegroundColor Yellow
        }
    }
    
    # Recreate with proper scope
    Set-Alias -Name rp -Value Reload-Profile -Scope Global -Force
    Set-Alias -Name ep -Value Edit-Profile -Scope Global -Force
}

# 3. Fix cursor position error
try {
    $RawUI = $Host.UI.RawUI
    $RawUI.CursorPosition = @{X = 0; Y = 0 }
} catch {
    # Suppress cursor position errors
    Add-Content -Path "$logDir\profile_errors.log" -Value "[$(Get-Date)] Cursor position error: $_"
}

# 4. Reload profile with error handling
function Reload-Profile {
    try {
        $profileFiles = @(
            $PROFILE.CurrentUserAllHosts,
            $PROFILE.CurrentUserCurrentHost,
            "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1",
            "$env:USERPROFILE\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
        )
        
        foreach ($file in $profileFiles) {
            if (Test-Path $file) {
                Write-Host "Loading profile: $file" -ForegroundColor Cyan
                . $file
            }
        }
        
        # Reset aliases after loading profiles
        Reset-Aliases
        
        Write-Host "Profile reloaded successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Error loading profile: $_" -ForegroundColor Red
        Add-Content -Path "$logDir\profile_errors.log" -Value "[$(Get-Date)] Profile reload error: $_"
    }
}

# 5. Initialize environment
Write-Host "=== Environment Initialized ===" -ForegroundColor Magenta
Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Cyan
Write-Host "Execution Policy: $(Get-ExecutionPolicy)" -ForegroundColor Cyan
Write-Host "Profile: $PROFILE" -ForegroundColor Cyan

# 6. Add helpful functions
function Edit-Profile {
    code $PROFILE.CurrentUserCurrentHost
}

# 7. Set up logging
function Write-SecureLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $logEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    $logFile = "$logDir\secure_$(Get-Date -Format 'yyyyMMdd').log"
    
    # Write to log file
    Add-Content -Path $logFile -Value $logEntry -ErrorAction SilentlyContinue
    
    # Color console output based on level
    switch ($Level) {
        "ERROR" { $color = "Red" }
        "WARN"  { $color = "Yellow" }
        "DEBUG" { $color = "Gray" }
        default { $color = "White" }
    }
    
    Write-Host $logEntry -ForegroundColor $color
}

# 8. Initialize security logging
Write-SecureLog "PowerShell session started" "INFO"

# 9. Display quick help
function Show-QuickHelp {
    Write-Host "`n=== Quick Help ===" -ForegroundColor Magenta
    Write-Host "rp           - Reload PowerShell profile" -ForegroundColor Cyan
    Write-Host "ep           - Edit PowerShell profile" -ForegroundColor Cyan
    Write-Host "Get-Help     - Get help for commands" -ForegroundColor Cyan
    Write-Host "Get-Command  - Find commands" -ForegroundColor Cyan
    Write-Host "Get-Alias    - List aliases" -ForegroundColor Cyan
}

# 10. Set window title
$Host.UI.RawUI.WindowTitle = "Secure PowerShell - $env:USERNAME@$env:COMPUTERNAME"

# 11. Set secure environment variables
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + 
            [System.Environment]::GetEnvironmentVariable("Path", "User")

# 12. Initialize completion
Set-PSReadLineKeyHandler -Key Tab -Function Complete
Set-PSReadLineOption -PredictionSource History

# 13. Display quick help on startup
Show-QuickHelp

Write-Host "`nEnvironment ready. Type 'Show-QuickHelp' to see available commands." -ForegroundColor Green
