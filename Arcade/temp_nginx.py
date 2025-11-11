    def _configure_nginx(self, enable_ssl: bool = False, domain: str = None) -> bool:
        """Configure nginx reverse proxy."""
        print("🌐 Configuring nginx...")

        try:
            listen_config = ""
            ssl_config = ""

            if enable_ssl and domain:
                # SSL configuration
                listen_config = """
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Redirect HTTP to HTTPS
    if ($scheme != "https") {
        return 301 https://$host$request_uri;
    }
"""
                ssl_config = f"""
server {{
    listen 80;
    listen [::]:80;
    server_name {domain};
    return 301 https://{domain}$request_uri;
}}
"""
            else:
                listen_config = """
    listen 80;
    listen [::]:80;
"""

            nginx_config = f"""
server {{
    {listen_config}
    server_name localhost;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {{
        proxy_pass http://127.0.0.1:7681;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}

    # Static files (if any)
    location /static {{
        alias /opt/atmosphere-arcade/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Logs
    access_log /var/log/nginx/atmosphere-arcade_access.log;
    error_log /var/log/nginx/atmosphere-arcade_error.log;
}}
{ssl_config}
"""

            config_path = Path('/etc/nginx/sites-available/atmosphere-arcade')
            enabled_path = Path('/etc/nginx/sites-enabled/atmosphere-arcade')

            # Backup existing config if it exists
            if config_path.exists():
                backup_path = Path(f'/etc/nginx/sites-available/atmosphere-arcade.backup.{int(time.time())}')
                if not self.run_sudo_command(['cp', str(config_path), str(backup_path)], f"Backing up existing nginx config to {backup_path}"):
                    print("⚠️ Backup failed, but continuing...")

            # Write config file securely
            temp_config = Path(f'/tmp/atmosphere-arcade-nginx.{int(time.time())}')
            temp_config.write_text(nginx_config)

            if not self.run_sudo_command(['mv', str(temp_config), str(config_path)], "Installing nginx config file"):
                temp_config.unlink()
                return False

            # Set proper permissions
            if not self.run_sudo_command(['chmod', '644', str(config_path)], "Setting nginx config permissions"):
                return False

            # Enable site (remove old symlink first)
            if enabled_path.exists():
                if not self.run_sudo_command(['rm', '-f', str(enabled_path)], "Removing old nginx site symlink"):
                    return False

            if not self.run_sudo_command(['ln', '-sf', str(config_path), str(enabled_path)], "Enabling nginx site"):
                return False

            # Test nginx configuration
            if not self.run_sudo_command(['nginx', '-t'], "Testing nginx configuration"):
                return False

            print("✅ Nginx configured")
            if enable_ssl:
                print("   🔒 SSL/HTTPS enabled")
            else:
                print("   ⚠️  HTTP only (consider enabling SSL for production)")

            return True

        except Exception as e:
            print(f"❌ Nginx configuration failed: {e}")
            return False
