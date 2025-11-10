# Audio Module for Atmosphere Project

# Import private functions
$privateFunctions = @(
    'Private\Invoke-AudioPreprocessing.ps1',
    'Private\Test-AudioFileFormat.ps1',
    'Private\Convert-AudioFormat.ps1'
)

foreach ($function in $privateFunctions) {
    try {
        . (Join-Path -Path $PSScriptRoot -ChildPath $function)
    } catch {
        Write-Error "Failed to import function $($function): $_"
    }
}

# Import public functions
$publicFunctions = @(
    'Public\Invoke-AudioAnalysis.ps1',
    'Public\Start-AudioProcessing.ps1',
    'Public\Measure-AudioQuality.ps1',
    'Public\Export-AudioReport.ps1'
)

foreach ($function in $publicFunctions) {
    try {
        . (Join-Path -Path $PSScriptRoot -ChildPath $function)
    } catch {
        Write-Error "Failed to import function $($function): $_"
    }
}

# Export public functions
export-modulemember -Function @(
    'Invoke-AudioAnalysis',
    'Start-AudioProcessing',
    'Measure-AudioQuality',
    'Export-AudioReport'
)

# Initialize module
$script:ModuleInitialized = $false

function Initialize-AudioModule {
    [CmdletBinding()]
    param()
    
    if (-not $script:ModuleInitialized) {
        Write-Log -Message 'Initializing Audio module...' -Level Debug -Source 'AudioModule'
        
        # Load configuration
        if ($script:Config.Audio) {
            $script:AudioConfig = $script:Config.Audio
        } else {
            $script:AudioConfig = @{
                SupportedFormats = @('.wav', '.mp3', '.flac', '.aiff')
                DefaultSampleRate = 44100
                DefaultChannels = 2
                DefaultBitDepth = 16
            }
        }
        
        $script:ModuleInitialized = $true
        Write-Log -Message 'Audio module initialized' -Level Debug -Source 'AudioModule'
    }
}

# Initialize the module when imported
Initialize-AudioModule
