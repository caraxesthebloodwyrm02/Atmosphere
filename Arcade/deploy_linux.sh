#!/bin/bash
# Atmosphere Arcade - Linux Deployment Script
# ===========================================

set -e

# Configuration
APP_NAME="atmosphere-arcade"
INSTALL_DIR="/opt/$APP_NAME"
SERVICE_NAME="$APP_NAME"
USER_NAME="$APP_NAME"
PYTHON_VERSION="3.10"

echo "🚀 Atmosphere Arcade - Linux Deployment"
echo "========================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons."
   echo "Please run as a regular user with sudo privileges."
   exit 1
fi

# Function to check command success
check_command() {
    if [ $? -ne 0 ]; then
        echo "❌ Command failed: $1"
        exit 1
    fi
}

# Update system
echo "📦 Updating system packages..."
sudo apt update
check_command "apt update"

sudo apt upgrade -y
check_command "apt upgrade"

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx
check_command "apt install"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user --upgrade pip
check_command "pip upgrade"

pip3 install --user fastapi uvicorn python-dotenv openai rich click textual
check_command "pip install"

# Create application user
echo "👤 Creating application user..."
sudo useradd -r -s /bin/false $USER_NAME 2>/dev/null || true

# Create installation directory
echo "📁 Creating installation directory..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR
check_command "mkdir install dir"

# Copy application files
echo "📋 Copying application files..."
cp -r . $INSTALL_DIR/
check_command "copy files"

# Set proper permissions
sudo chown -R $USER_NAME:$USER_NAME $INSTALL_DIR
sudo chmod -R 755 $INSTALL_DIR
check_command "set permissions"

# Create virtual environment
echo "🔧 Creating virtual environment..."
sudo -u $USER_NAME python3 -m venv $INSTALL_DIR/venv
check_command "create venv"

# Install dependencies in virtual environment
echo "📦 Installing dependencies in virtual environment..."
sudo -u $USER_NAME $INSTALL_DIR/venv/bin/pip install -r $INSTALL_DIR/requirements.txt
check_command "install dependencies"

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Atmosphere Arcade AI Terminal
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python start_arcade.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$APP_NAME

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
check_command "systemd setup"

# Create nginx configuration
echo "🌐 Configuring nginx..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:7681;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files
    location /static {
        alias $INSTALL_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/${APP_NAME}_access.log;
    error_log /var/log/nginx/${APP_NAME}_error.log;
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo nginx -t
check_command "nginx config"

sudo systemctl reload nginx
check_command "nginx reload"

# Create environment file template
echo "🔐 Creating environment configuration..."
sudo tee $INSTALL_DIR/.env.example > /dev/null <<EOF
# Atmosphere Arcade Configuration
# Copy this file to .env and fill in your values

# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
ARCADE_HOST=127.0.0.1
ARCADE_PORT=7681
ARCADE_DEBUG=false

# Security Settings
ARCADE_SECRET_KEY=your_secret_key_here
ARCADE_ALLOWED_HOSTS=localhost,127.0.0.1

# File System Settings
ARCADE_SANDBOX_PATH=/tmp/arcade_sandbox
ARCADE_MAX_FILE_SIZE=10485760
ARCADE_ALLOWED_EXTENSIONS=txt,py,md,json,yml,yaml

# AI Settings
ARCADE_AI_MODEL=gpt-4
ARCADE_AI_TEMPERATURE=0.8
ARCADE_AI_MAX_TOKENS=2000

# Multilingual Settings
ARCADE_DEFAULT_LANGUAGE=en
ARCADE_SUPPORTED_LANGUAGES=en,es,fr,de,bn,hi,ar,ja

# Monitoring
ARCADE_ENABLE_METRICS=true
ARCADE_LOG_LEVEL=INFO
ARCADE_METRICS_PORT=9090
EOF

# Set proper permissions for env file
sudo chown $USER_NAME:$USER_NAME $INSTALL_DIR/.env.example
sudo chmod 600 $INSTALL_DIR/.env.example

# Create log directory
sudo mkdir -p /var/log/$APP_NAME
sudo chown $USER_NAME:$USER_NAME /var/log/$APP_NAME

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy $INSTALL_DIR/.env.example to $INSTALL_DIR/.env"
echo "2. Edit $INSTALL_DIR/.env with your configuration"
echo "3. Start the service: sudo systemctl start $SERVICE_NAME"
echo "4. Check status: sudo systemctl status $SERVICE_NAME"
echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🌐 Web interface will be available at: http://localhost"
echo "🔌 API will be available at: http://localhost:7681"
echo ""
echo "📚 For SSL setup with Let's Encrypt:"
echo "sudo certbot --nginx -d yourdomain.com"
echo ""
echo "🆘 For troubleshooting:"
echo "- Check service status: sudo systemctl status $SERVICE_NAME"
echo "- Check nginx status: sudo systemctl status nginx"
echo "- View application logs: sudo journalctl -u $SERVICE_NAME -f"
echo "- View nginx logs: sudo tail -f /var/log/nginx/${APP_NAME}_*.log"
