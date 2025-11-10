# Core module for Atmosphere automation framework

# Initialize module variables
$script:ModuleRoot = $PSScriptRoot
$script:Config = @{}
$script:Initialized = $false

# Import private functions
$privateFunctions = @(
    'Private\Initialize-Configuration.ps1',
    'Private\Write-Log.ps1',
    'Private\Test-IsAdmin.ps1',
    'Private\Invoke-WithRetry.ps1'
)

foreach ($function in $privateFunctions) {
    try {
        . (Join-Path -Path $PSScriptRoot -ChildPath $function)
    } catch {
        Write-Error "Failed to import function $function : $_"
    }
}

# Import public functions
$publicFunctions = @(
    'Public\Initialize-Atmosphere.ps1',
    'Public\Get-ProjectStatus.ps1',
    'Public\Invoke-ProjectBuild.ps1',
    'Public\Start-ProjectTest.ps1',
    'Public\Invoke-ProjectDeploy.ps1',
    'Public\Start-ProjectMonitor.ps1'
)

foreach ($function in $publicFunctions) {
    try {
        . (Join-Path -Path $PSScriptRoot -ChildPath $function)
    } catch {
        Write-Error "Failed to import function $function : $_"
    }
}

# Export public functions
export-modulemember -Function @(
    'Initialize-Atmosphere',
    'Get-ProjectStatus',
    'Invoke-ProjectBuild',
    'Start-ProjectTest',
    'Invoke-ProjectDeploy',
    'Start-ProjectMonitor'
)

# Initialize the module if not already initialized
if (-not $script:Initialized) {
    Initialize-Atmosphere -ErrorAction SilentlyContinue
}
