<#
.SYNOPSIS
    Sets up the Atmosphere automation framework.
.DESCRIPTION
    This script sets up the necessary environment for the Atmosphere automation framework,
    including module path configuration and initial setup tasks.
#>

[CmdletBinding()]
param (
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Update,
    [string]$ProfilePath = $PROFILE.CurrentUserAllHosts
)

# Ensure we're running with admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Set up paths
$modulePath = Join-Path -Path $PSScriptRoot -ChildPath 'modules'
$configPath = Join-Path -Path $PSScriptRoot -ChildPath 'config'
$logPath = Join-Path -Path $PSScriptRoot -ChildPath 'logs'

# Create required directories
$requiredDirs = @($modulePath, $configPath, $logPath)
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Add module path to PSModulePath if not already present
$modulePaths = $env:PSModulePath -split ';'
if ($modulePaths -notcontains $modulePath) {
    $env:PSModulePath = "$modulePath;" + $env:PSModulePath
    Write-Host "Added $modulePath to PSModulePath" -ForegroundColor Green
}

# Create or update profile
if ($Install) {
    $profileContent = @"
# Atmosphere Automation Framework
`$modulePath = "$modulePath"
if (`$env:PSModulePath -notlike "*`$modulePath*") {
    `$env:PSModulePath = "`$modulePath;" + `$env:PSModulePath
}

# Import Atmosphere module
Import-Module Atmosphere -Force -ErrorAction SilentlyContinue

# Initialize the framework
try {
    Initialize-Atmosphere -ErrorAction Stop
    Write-Host "Atmosphere automation framework initialized successfully" -ForegroundColor Green
} catch {
    Write-Warning "Failed to initialize Atmosphere: `$(`_.Exception.Message)"
}
"@

    # Create the profile directory if it doesn't exist
    $profileDir = Split-Path -Path $ProfilePath -Parent
    if (-not (Test-Path -Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }

    # Append to existing profile or create new one
    if (Test-Path -Path $ProfilePath) {
        $existingContent = Get-Content -Path $ProfilePath -Raw
        if ($existingContent -notmatch 'Atmosphere Automation Framework') {
            $profileContent | Add-Content -Path $ProfilePath -Force
            Write-Host "Updated profile at $ProfilePath" -ForegroundColor Green
        } else {
            Write-Host "Atmosphere is already configured in your profile" -ForegroundColor Yellow
        }
    } else {
        $profileContent | Set-Content -Path $ProfilePath -Force
        Write-Host "Created profile at $ProfilePath" -ForegroundColor Green
    }
}

# Uninstall logic
if ($Uninstall) {
    if (Test-Path -Path $ProfilePath) {
        $content = Get-Content -Path $ProfilePath -Raw
        $newContent = $content -replace '(?s)# Atmosphere Automation Framework.*?Atmosphere automation framework initialized successfully[^\r\n]*\r?\n', ''
        
        if ($content -ne $newContent) {
            $newContent | Set-Content -Path $ProfilePath -Force
            Write-Host "Removed Atmosphere configuration from profile" -ForegroundColor Green
        } else {
            Write-Host "No Atmosphere configuration found in profile" -ForegroundColor Yellow
        }
    }
    
    # Remove module path from PSModulePath
    $env:PSModulePath = ($env:PSModulePath -split ';' | Where-Object { $_ -ne $modulePath }) -join ';'
    [Environment]::SetEnvironmentVariable('PSModulePath', $env:PSModulePath, 'User')
    
    Write-Host "Atmosphere framework has been uninstalled" -ForegroundColor Green
    exit 0
}

# Update logic
if ($Update) {
    # This would typically pull the latest version from a repository
    Write-Host "Updating Atmosphere framework..." -ForegroundColor Cyan
    # Add update logic here (e.g., git pull, download from URL, etc.)
    Write-Host "Update functionality not yet implemented" -ForegroundColor Yellow
    exit 0
}

# If no parameters, just initialize the framework
Write-Host "Setting up Atmosphere automation framework..." -ForegroundColor Cyan
Write-Host "Module path: $modulePath"
Write-Host "Config path: $configPath"
Write-Host "Log path: $logPath"

# Import the module
Import-Module -Name (Join-Path -Path $modulePath -ChildPath 'Core\Atmosphere.psd1') -Force -ErrorAction Stop

# Initialize the framework
try {
    Initialize-Atmosphere -ErrorAction Stop
    Write-Host "Atmosphere automation framework initialized successfully" -ForegroundColor Green
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Run '.\setup.ps1 -Install' to add to your PowerShell profile"
    Write-Host "2. Use 'Get-Command -Module Atmosphere' to see available commands"
    Write-Host "3. Run 'Get-ProjectStatus' to check the project status"
    
} catch {
    Write-Error "Failed to initialize Atmosphere framework: $_"
    exit 1
}
