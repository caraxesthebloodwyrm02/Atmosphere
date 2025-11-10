function Initialize-Configuration {
    [CmdletBinding()]
    param(
        [string]$ConfigPath = (Join-Path -Path $PSScriptRoot -ChildPath '..\..\config\atmosphere.config.json')
    )

    # Default configuration
    $defaultConfig = @{
        Logging = @{
            LogPath = Join-Path -Path $PSScriptRoot -ChildPath '..\..\logs'
            LogLevel = 'Information'  # Debug, Information, Warning, Error
            MaxLogAge = 30  # days
            MaxLogSizeMB = 10
        }
        Build = @{
            OutputDirectory = Join-Path -Path $PSScriptRoot -ChildPath '..\..\build'
            CleanBeforeBuild = $true
            Configuration = 'Debug'  # Debug or Release
        }
        Deploy = @{
            Environments = @{
                Dev = @{
                    Name = 'Development'
                    Type = 'Local'
                    Path = Join-Path -Path $PSScriptRoot -ChildPath '..\..\deploy\dev'
                }
                Prod = @{
                    Name = 'Production'
                    Type = 'Remote'
                    Path = '\\server\deploy\prod'
                }
            }
        }
        Audio = @{
            SupportedFormats = @('.wav', '.mp3', '.flac', '.aiff')
            DefaultSampleRate = 44100
            DefaultChannels = 2
            DefaultBitDepth = 16
        }
    }

    # Create config directory if it doesn't exist
    $configDir = Split-Path -Path $ConfigPath -Parent
    if (-not (Test-Path -Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }

    # Load existing config or create default
    if (Test-Path -Path $ConfigPath) {
        try {
            $config = Get-Content -Path $ConfigPath -Raw -ErrorAction Stop | ConvertFrom-Json -AsHashtable -ErrorAction Stop
            
            # Merge with defaults (new settings will be added, existing ones preserved)
            $script:Config = Merge-Hashtables -Source $defaultConfig, $config
        } catch {
            Write-Warning "Failed to load config file: $_"
            $script:Config = $defaultConfig
        }
    } else {
        $script:Config = $defaultConfig
        
        # Save default config
        $script:Config | ConvertTo-Json -Depth 10 | Out-File -FilePath $ConfigPath -Force
    }

    # Ensure required directories exist
    $requiredDirs = @(
        $script:Config.Logging.LogPath,
        $script:Config.Build.OutputDirectory
    )

    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path -Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    return $script:Config
}
