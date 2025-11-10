function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter()]
        [ValidateSet('Debug', 'Information', 'Warning', 'Error')]
        [string]$Level = 'Information',
        
        [Parameter()]
        [string]$LogName = 'Atmosphere',
        
        [Parameter()]
        [string]$Source = (Get-PSCallStack)[1].Command
    )
    
    # Skip if logging isn't initialized yet
    if (-not $script:Config -or -not $script:Config.Logging) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
        return
    }
    
    $logLevels = @{
        'Debug' = 0
        'Information' = 1
        'Warning' = 2
        'Error' = 3
    }
    
    $currentLevel = $script:Config.Logging.LogLevel
    $currentLevelValue = $logLevels[$currentLevel]
    $messageLevelValue = $logLevels[$Level]
    
    # Skip if message level is below the configured log level
    if ($messageLevelValue -lt $currentLevelValue) {
        return
    }
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logEntry = "[$timestamp] [$($Level.ToUpper())] [$Source] $Message"
    
    # Ensure log directory exists
    $logDir = $script:Config.Logging.LogPath
    if (-not (Test-Path -Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    # Rotate logs if needed
    $logFile = Join-Path -Path $logDir -ChildPath "${LogName}_$(Get-Date -Format 'yyyyMMdd').log"
    
    # Check if log file exists and is too large
    if (Test-Path -Path $logFile) {
        $logSize = (Get-Item -Path $logFile).Length / 1MB
        if ($logSize -gt $script:Config.Logging.MaxLogSizeMB) {
            $archiveFile = $logFile -replace '\.log$', "_$(Get-Date -Format 'yyyyMMddHHmmss').log"
            Move-Item -Path $logFile -Destination $archiveFile -Force
        }
    }
    
    # Write to log file
    try {
        Add-Content -Path $logFile -Value $logEntry -ErrorAction Stop
    } catch {
        Write-Host "Failed to write to log file: $_" -ForegroundColor Red
        Write-Host $logEntry
    }
    
    # Also write to console with appropriate colors
    $colors = @{
        'DEBUG' = 'Gray'
        'INFORMATION' = 'White'
        'WARNING' = 'Yellow'
        'ERROR' = 'Red'
    }
    
    $color = $colors[$Level.ToUpper()]
    Write-Host $logEntry -ForegroundColor $color
    
    # For errors, write to error stream
    if ($Level -eq 'Error') {
        Write-Error -Message $Message -ErrorAction Continue
    }
}

# Helper function for logging exceptions
function Write-Exception {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [System.Management.Automation.ErrorRecord]$Exception,
        
        [string]$Message = 'An error occurred',
        
        [string]$Source = (Get-PSCallStack)[1].Command
    )
    
    $errorMessage = @"
$Message
Exception Type: $($Exception.Exception.GetType().FullName)
Error Message: $($Exception.Exception.Message)
Stack Trace:
$($Exception.ScriptStackTrace)
"@
    
    Write-Log -Message $errorMessage -Level Error -Source $Source
}
