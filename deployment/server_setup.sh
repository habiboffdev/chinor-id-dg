#!/bin/bash

# Server setup script for DigitalOcean Droplet
# Run this as root on a fresh Ubuntu 22.04 droplet

echo "🖥️  Setting up DigitalOcean server for Opportuni MVP..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

print_step "1. Updating system packages..."
apt update && apt upgrade -y

print_step "2. Installing essential packages..."
apt install -y software-properties-common curl wget git unzip

print_step "3. Installing Python and development tools..."
apt install -y python3 python3-pip python3-venv python3-dev build-essential

print_step "4. Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib

print_step "5. Installing Nginx..."
apt install -y nginx

print_step "6. Installing Supervisor..."
apt install -y supervisor

print_step "7. Installing Certbot for SSL..."
apt install -y certbot python3-certbot-nginx

print_step "8. Creating opportuni user..."
if ! id "opportuni" &>/dev/null; then
    adduser --disabled-password --gecos "" opportuni
    usermod -aG sudo opportuni
    print_status "Created user: opportuni"
else
    print_warning "User opportuni already exists"
fi

print_step "9. Setting up PostgreSQL database..."
sudo -u postgres createdb opportuni_db 2>/dev/null || print_warning "Database already exists"
sudo -u postgres createuser opportuni_user 2>/dev/null || print_warning "User already exists"

# Generate a random password for the database
DB_PASSWORD=$(openssl rand -base64 32)
sudo -u postgres psql -c "ALTER USER opportuni_user WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE opportuni_db TO opportuni_user;"

print_step "10. Creating log directories..."
mkdir -p /var/log/opportuni
chown opportuni:opportuni /var/log/opportuni

print_step "11. Setting up firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

print_step "12. Creating SSH key directory for opportuni user..."
sudo -u opportuni mkdir -p /home/opportuni/.ssh
sudo -u opportuni chmod 700 /home/opportuni/.ssh

print_status "✅ Server setup completed!"
echo ""
echo "📝 IMPORTANT INFORMATION:"
echo "========================="
echo "Database Password: $DB_PASSWORD"
echo "Save this password - you'll need it for the .env file!"
echo ""
echo "Next steps:"
echo "1. Copy your SSH public key to /home/opportuni/.ssh/authorized_keys"
echo "2. Clone your repository to /home/opportuni/opportuni"
echo "3. Run the deployment script as the opportuni user"
echo ""
echo "🔑 To add your SSH key:"
echo "sudo -u opportuni nano /home/opportuni/.ssh/authorized_keys"
echo ""
echo "🔐 To switch to opportuni user:"
echo "su - opportuni"
