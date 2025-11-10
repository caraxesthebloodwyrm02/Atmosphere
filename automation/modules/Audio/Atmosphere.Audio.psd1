@{
    # Script module or binary module file associated with this manifest.
    RootModule = 'Atmosphere.Audio.psm1'
    
    # Version number of this module.
    ModuleVersion = '0.1.0'
    
    # Supported PSEditions
    CompatiblePSEditions = @('Core', 'Desktop')
    
    # ID used to uniquely identify this module
    GUID = 'a2b3c4d5-2345-6789-01ab-cdef12345678'
    
    # Author of this module
    Author = 'Atmosphere Team'
    
    # Company or vendor of this module
    CompanyName = 'Atmosphere Project'
    
    # Copyright statement for this module
    Copyright = '(c) 2025 Atmosphere Project. All rights reserved.'
    
    # Description of the functionality provided by this module
    Description = 'Audio processing and analysis module for the Atmosphere project'
    
    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '5.1'
    
    # Modules that must be imported into the global environment prior to importing this module
    RequiredModules = @('Atmosphere.Core')
    
    # Functions to export from this module
    FunctionsToExport = @(
        'Invoke-AudioAnalysis',
        'Start-AudioProcessing',
        'Measure-AudioQuality',
        'Export-AudioReport'
    )
    
    # Private data to pass to the module
    PrivateData = @{
        PSData = @{
            Tags = @('Audio', 'Processing', 'Analysis', 'Atmosphere')
            LicenseUri = 'https://github.com/yourusername/atmosphere/blob/main/LICENSE'
            ProjectUri = 'https://github.com/yourusername/atmosphere'
        }
    }
}
