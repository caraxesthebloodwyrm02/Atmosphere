# Atmosphere Arcade - Secure Production Deployment
# ===============================================

## Overview

This deployment system provides **enterprise-grade security** for Atmosphere Arcade production deployments with comprehensive safety measures and rollback capabilities.

## Security Features

### ✅ Enterprise Security Standards
- **Sudo Access Validation**: Confirms privileged access before operations
- **Automatic Backups**: Creates timestamped backups before destructive operations
- **Atomic File Operations**: Write to temporary files, then atomic move
- **Secure Permissions**: Proper file ownership and access controls
- **Service Sandboxing**: systemd restrictions prevent privilege escalation
- **Input Validation**: All operations validated before execution

### ✅ Safety Measures
- **Non-Destructive Defaults**: Requires explicit confirmation for overwrites
- **Comprehensive Logging**: All operations logged with timestamps
- **Timeout Protection**: All commands have timeout limits
- **Error Recovery**: Failed operations don't leave system in inconsistent state
- **Rollback Support**: Backup restoration capabilities

## Deployment Types

### 🐍 Basic Deployment (Safest)
**Target**: Development/Testing environments
**Security Level**: High (no sudo required)
**Features**: Local Python installation with virtual environment

```bash
python deploy_production.py basic
```

**What it does:**
- ✅ Validates environment and dependencies
- ✅ Creates isolated virtual environment
- ✅ Installs application securely
- ✅ Generates startup scripts
- ✅ No system modifications

### 🏭 Production Deployment (Linux)
**Target**: Production Linux servers
**Security Level**: Maximum
**Features**: Systemd service, nginx reverse proxy, monitoring

```bash
sudo python deploy_production.py production
```

**Security Features:**
- ✅ Sudo access validation
- ✅ Automatic backup creation
- ✅ Secure service configuration
- ✅ Sandboxed execution environment
- ✅ Log rotation and monitoring

### 🏢 Enterprise Deployment (Advanced)
**Target**: Enterprise environments with monitoring
**Security Level**: Maximum
**Features**: All production features plus advanced monitoring

```bash
sudo python deploy_production.py enterprise
```

## Pre-Deployment Checklist

### 🔐 Security Prerequisites
- [ ] **Sudo Access**: `sudo -n true` works without password prompt
- [ ] **API Keys**: `OPENAI_API_KEY` environment variable set
- [ ] **Backup Space**: Sufficient disk space for backups
- [ ] **Network**: Outbound HTTPS access for package downloads

### 🖥️ System Requirements
- [ ] **OS**: Ubuntu 20.04+ or Debian 11+ (recommended)
- [ ] **Python**: 3.8+ installed
- [ ] **Disk Space**: 2GB free for installation + backups
- [ ] **Memory**: 2GB RAM minimum, 4GB recommended

### 📋 Application Requirements
- [ ] **Dependencies**: All Python packages in requirements.txt
- [ ] **Permissions**: Write access to installation directories
- [ ] **Services**: systemd available and functional
- [ ] **Firewall**: Ports 80, 7681 available

## Secure Deployment Process

### Phase 1: Pre-Flight Checks
```bash
# 1. Validate environment
python deploy_production.py --show-options

# 2. Check prerequisites (manual)
sudo -n true  # Test sudo access
echo $OPENAI_API_KEY  # Verify API key
df -h  # Check disk space
```

### Phase 2: Safe Deployment
```bash
# For production deployment:
sudo python deploy_production.py production

# Script automatically:
# ✅ Validates sudo access
# ✅ Creates backups (/opt/atmosphere-arcade-backup-{timestamp}/)
# ✅ Installs system dependencies securely
# ✅ Configures systemd with sandboxing
# ✅ Sets up nginx with security headers
# ✅ Tests deployment before completion
```

### Phase 3: Post-Deployment Validation
```bash
# Check service status
sudo systemctl status atmosphere-arcade
sudo systemctl status nginx

# Test application
curl http://localhost/health
curl http://localhost:7681/docs

# Verify logs
sudo journalctl -u atmosphere-arcade -n 50
sudo tail /var/log/nginx/atmosphere-arcade*.log
```

## Security Configurations Applied

### Systemd Service Security
```ini
[Service]
User=www-data
ProtectHome=true
NoNewPrivileges=true
PrivateTmp=true
```

### Nginx Security Headers
```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
```

### File Permissions
```bash
# Application files: 755 (www-data ownership)
# Config files: 644 (root ownership)
# Logs: 644 (www-data ownership)
```

## Backup and Recovery

### Automatic Backups
The deployment script automatically creates backups:
```
/opt/atmosphere-arcade-backup-{timestamp}/
├── app/           # Application files
├── config/        # Configuration files
├── logs/          # Log files
└── backup-info.txt # Backup metadata
```

### Manual Recovery
```bash
# Stop services
sudo systemctl stop atmosphere-arcade nginx

# Restore from backup
sudo cp -r /opt/atmosphere-arcade-backup-{timestamp}/* /opt/atmosphere-arcade/

# Restart services
sudo systemctl start atmosphere-arcade
sudo systemctl reload nginx
```

## Monitoring and Maintenance

### Service Monitoring
```bash
# Check service health
sudo systemctl status atmosphere-arcade

# View logs
sudo journalctl -u atmosphere-arcade -f

# Restart service
sudo systemctl restart atmosphere-arcade
```

### Log Management
```bash
# Application logs
sudo tail -f /var/log/atmosphere-arcade/*.log

# Nginx logs
sudo tail -f /var/log/nginx/atmosphere-arcade*.log

# Log rotation (automatic)
sudo logrotate /etc/logrotate.d/atmosphere-arcade
```

## Troubleshooting

### Common Issues

#### Sudo Access Denied
```bash
# Solution: Configure passwordless sudo or run manually
sudo visudo  # Add: username ALL=(ALL) NOPASSWD: ALL
```

#### Service Won't Start
```bash
# Check logs
sudo journalctl -u atmosphere-arcade -n 50

# Test manually
cd /opt/atmosphere-arcade
source venv/bin/activate
python start_arcade.py --check
```

#### Nginx Configuration Error
```bash
# Test config
sudo nginx -t

# Check error logs
sudo tail /var/log/nginx/error.log
```

#### Port Conflicts
```bash
# Check port usage
sudo netstat -tulpn | grep :7681
sudo netstat -tulpn | grep :80

# Change ports in configuration if needed
```

## Security Best Practices

### 🔐 Hardening Recommendations

#### 1. Network Security
```bash
# Install firewall
sudo ufw enable
sudo ufw allow 80
sudo ufw allow 443

# Use SSL/TLS (recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### 2. System Security
```bash
# Regular updates
sudo apt update && sudo apt upgrade

# Disable root login
sudo passwd -l root

# Use fail2ban for SSH protection
sudo apt install fail2ban
```

#### 3. Application Security
```bash
# Regular backups
sudo cp -r /opt/atmosphere-arcade /opt/atmosphere-arcade-backup-$(date +%Y%m%d)

# Monitor logs
sudo logwatch --detail High --range Today
```

### 📊 Monitoring Setup

#### Basic Monitoring
```bash
# System monitoring
sudo apt install htop iotop

# Application monitoring
curl -f http://localhost/health || echo "Service down"
```

#### Advanced Monitoring (Optional)
```bash
# Prometheus + Grafana setup
sudo docker-compose -f monitoring/docker-compose.yml up -d
```

## Emergency Procedures

### Service Down
```bash
# Quick restart
sudo systemctl restart atmosphere-arcade

# Check dependencies
sudo systemctl status nginx postgresql redis

# Full system check
sudo python deploy_production.py production  # Re-run deployment
```

### Data Loss
```bash
# Restore from backup
sudo systemctl stop atmosphere-arcade
sudo cp -r /opt/atmosphere-arcade-backup-{timestamp}/* /opt/atmosphere-arcade/
sudo systemctl start atmosphere-arcade
```

### Security Incident
```bash
# Immediate actions
sudo systemctl stop atmosphere-arcade nginx
sudo ufw --force enable  # Block all traffic

# Investigate logs
sudo journalctl -u atmosphere-arcade --since "1 hour ago"
sudo ausearch -m all --start recent

# Rebuild from clean backup
sudo python deploy_production.py production --force
```

## Support and Documentation

### 📚 Documentation Resources
- **README.md**: Complete user guide
- **API_REFERENCE.md**: API documentation
- **SECURITY_IMPLEMENTATION.md**: Security details
- **deploy_production.py**: Self-documenting deployment script

### 🆘 Getting Help
1. Check logs: `sudo journalctl -u atmosphere-arcade`
2. Test manually: `cd /opt/atmosphere-arcade && source venv/bin/activate && python start_arcade.py --check`
3. Review documentation in `/opt/atmosphere-arcade/docs/`
4. Check system resources: `df -h && free -h`

---

## Summary

This deployment system provides **enterprise-grade security** with:
- ✅ **Comprehensive backups** before destructive operations
- ✅ **Sudo validation** before privileged operations
- ✅ **Atomic file operations** to prevent corruption
- ✅ **Service sandboxing** to prevent privilege escalation
- ✅ **Security headers** and proper permissions
- ✅ **Monitoring and logging** for operational visibility
- ✅ **Rollback capabilities** for failed deployments

**The deployment is designed to be safe, secure, and production-ready while maintaining the highest standards of system administration best practices.**
