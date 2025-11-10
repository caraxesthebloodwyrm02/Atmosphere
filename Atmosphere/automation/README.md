# Project Automation Framework

This is the core automation framework for the Atmosphere project. It provides a set of PowerShell modules and scripts to automate common development and maintenance tasks.

## Structure

```
automation/
├── modules/               # PowerShell modules
│   ├── Core/             # Core functionality
│   ├── Audio/            # Audio processing tasks
│   ├── Dev/              # Development tools
│   └── Utils/            # Utility functions
├── scripts/              # Standalone scripts
├── config/               # Configuration files
├── logs/                 # Log files
└── tests/                # Pester tests
```

## Getting Started

1. Run the setup script to configure your environment:
   ```powershell
   .\setup.ps1
   ```

2. Import the main module:
   ```powershell
   Import-Module .\modules\Core\Atmosphere.psd1 -Force
   ```

## Available Commands

- `Invoke-ProjectBuild` - Build the project
- `Start-ProjectTest` - Run tests
- `Invoke-ProjectDeploy` - Deploy the project
- `Get-ProjectStatus` - Get project status
- `Start-ProjectMonitor` - Monitor project resources

## Contributing

1. Add new modules to the `modules` directory
2. Update documentation in the relevant module
3. Add tests in the `tests` directory
4. Submit a pull request
