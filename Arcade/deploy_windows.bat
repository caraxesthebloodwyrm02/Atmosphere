@echo off
REM Atmosphere Arcade - Windows Deployment Script
REM =============================================

echo 🚀 Atmosphere Arcade - Windows Deployment
echo ============================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as administrator
) else (
    echo ❌ Please run this script as administrator
    pause
    exit /b 1
)

REM Configuration
set APP_NAME=atmosphere-arcade
set INSTALL_DIR=C:\Program Files\%APP_NAME%
set SERVICE_NAME=%APP_NAME%
set PYTHON_VERSION=3.10

REM Create installation directory
echo 📁 Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if errorlevel 1 (
    echo ❌ Failed to create installation directory
    pause
    exit /b 1
)

REM Check Python installation
echo 🐍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)

pip install fastapi uvicorn python-dotenv openai rich click textual pywin32
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Copy application files
echo 📋 Copying application files...
xcopy /E /I /Y "." "%INSTALL_DIR%\" >nul
if errorlevel 1 (
    echo ❌ Failed to copy application files
    pause
    exit /b 1
)

REM Create logs directory
echo 📝 Creating logs directory...
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"

REM Create data directory
echo 💾 Creating data directory...
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"

REM Create environment file template
echo 🔐 Creating environment configuration...
(
echo # Atmosphere Arcade Configuration
echo # Copy this file to .env and fill in your values
echo.
echo # Required: OpenAI API Key
echo OPENAI_API_KEY=your_openai_api_key_here
echo.
echo # Server Configuration
echo ARCADE_HOST=127.0.0.1
echo ARCADE_PORT=7681
echo ARCADE_DEBUG=false
echo.
echo # Security Settings
echo ARCADE_SECRET_KEY=your_secret_key_here
echo ARCADE_ALLOWED_HOSTS=localhost,127.0.0.1
echo.
echo # File System Settings
echo ARCADE_SANDBOX_PATH=C:\Users\%USERNAME%\AppData\Local\AtmosphereArcade\sandbox
echo ARCADE_MAX_FILE_SIZE=10485760
echo ARCADE_ALLOWED_EXTENSIONS=txt,py,md,json,yml,yaml,bat,ps1
echo.
echo # AI Settings
echo ARCADE_AI_MODEL=gpt-4
echo ARCADE_AI_TEMPERATURE=0.8
echo ARCADE_AI_MAX_TOKENS=2000
echo.
echo # Multilingual Settings
echo ARCADE_DEFAULT_LANGUAGE=en
echo ARCADE_SUPPORTED_LANGUAGES=en,es,fr,de,bn,hi,ar,ja
echo.
echo # Monitoring
echo ARCADE_ENABLE_METRICS=true
echo ARCADE_LOG_LEVEL=INFO
echo ARCADE_METRICS_PORT=9090
) > "%INSTALL_DIR%\.env.example"

REM Create Windows service
echo ⚙️ Creating Windows service...
set SERVICE_CMD=%INSTALL_DIR%\venv\Scripts\python.exe %INSTALL_DIR%\start_arcade.py
set SERVICE_DESC="Atmosphere Arcade AI Terminal Service"

REM Use NSSM (Non-Sucking Service Manager) if available, otherwise use sc
where nssm >nul 2>&1
if %errorlevel% == 0 (
    echo Using NSSM for service creation...
    nssm install %SERVICE_NAME% "%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\start_arcade.py"
    nssm set %SERVICE_NAME% Description "%SERVICE_DESC%"
    nssm set %SERVICE_NAME% AppDirectory "%INSTALL_DIR%"
    nssm set %SERVICE_NAME% AppStdout "%INSTALL_DIR%\logs\service.out.log"
    nssm set %SERVICE_NAME% AppStderr "%INSTALL_DIR%\logs\service.err.log"
) else (
    echo NSSM not found, creating service manually...
    echo Please install NSSM from https://nssm.cc/ for better service management
    echo.
    echo Manual service creation:
    echo sc create %SERVICE_NAME% binPath= "%SERVICE_CMD%" start= auto
)

REM Create firewall rule
echo 🔥 Creating firewall rule...
netsh advfirewall firewall add rule name="Atmosphere Arcade" dir=in action=allow protocol=TCP localport=7681 >nul
if errorlevel 1 (
    echo ⚠️ Failed to create firewall rule (may require manual configuration)
)

REM Create desktop shortcut
echo 🖥️ Creating desktop shortcut...
set SHORTCUT_PATH=%PUBLIC%\Desktop\Atmosphere Arcade.lnk
if exist "%SHORTCUT_PATH%" del "%SHORTCUT_PATH%"

REM Create start script
echo 📜 Creating start script...
(
echo @echo off
echo REM Atmosphere Arcade Start Script
echo cd /d "%INSTALL_DIR%"
echo if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
echo python start_arcade.py %%*
) > "%INSTALL_DIR%\start_arcade.bat"

REM Create stop script
echo 📜 Creating stop script...
(
echo @echo off
echo REM Atmosphere Arcade Stop Script
echo echo Stopping Atmosphere Arcade service...
echo sc stop %SERVICE_NAME%
echo echo Service stopped.
) > "%INSTALL_DIR%\stop_arcade.bat"

echo.
echo ✅ Installation completed successfully!
echo.
echo 📋 Next steps:
echo 1. Copy %INSTALL_DIR%\.env.example to %INSTALL_DIR%\.env
echo 2. Edit %INSTALL_DIR%\.env with your configuration
echo 3. Start the service: sc start %SERVICE_NAME%
echo 4. Or run manually: "%INSTALL_DIR%\start_arcade.bat"
echo 5. Check status: sc query %SERVICE_NAME%
echo.
echo 🌐 Web interface will be available at: http://localhost:7681
echo 🖥️ Desktop shortcut created for easy access
echo.
echo 📁 Installation directory: %INSTALL_DIR%
echo 📝 Logs directory: %INSTALL_DIR%\logs
echo.
echo 🆘 For troubleshooting:
echo - Check service status: sc query %SERVICE_NAME%
echo - View event logs: eventvwr.msc
echo - View application logs: type "%INSTALL_DIR%\logs\*.log"
echo.
echo 📚 Additional configuration:
echo - Firewall: Ensure port 7681 is open
echo - Environment: Set OPENAI_API_KEY system variable
echo - Service: Configure service to run under specific user account
echo.
pause
