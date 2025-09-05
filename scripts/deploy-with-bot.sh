#!/bin/bash

echo "🚀 Deploying Opportuni with Telegram Bot"
echo "========================================"

# Configuration
REPO_DIR="/home/mirzosharif/MVP/chinor_id_new"
LOG_DIR="/var/log/opportuni"
SUPERVISOR_CONF="/etc/supervisor/conf.d/opportuni.conf"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Create log directory if it doesn't exist
log "📁 Creating log directory..."
sudo mkdir -p "$LOG_DIR"
sudo chown -R mirzosharif:mirzosharif "$LOG_DIR"

# Copy supervisor configuration
log "📋 Installing supervisor configuration..."
sudo cp "$REPO_DIR/deployment/supervisor.conf" "$SUPERVISOR_CONF"

# Reload supervisor configuration
log "🔄 Reloading supervisor..."
sudo supervisorctl reread
sudo supervisorctl update

# Install Python dependencies
log "📦 Installing dependencies..."
cd "$REPO_DIR"
source venv/bin/activate
pip install -r opportuni_backend/requirements.txt

# Install telegram bot dependencies if they exist
if [ -f "telegram_bot/requirements.txt" ]; then
    log "📦 Installing Telegram bot dependencies..."
    pip install -r telegram_bot/requirements.txt
fi

# Run migrations
log "🗃️  Running database migrations..."
cd opportuni_backend
python manage.py migrate

# Collect static files
log "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start services
log "🚀 Starting services..."
sudo supervisorctl start opportuni
sudo supervisorctl start opportuni_telegram_bot

# Check status
log "📊 Service status:"
sudo supervisorctl status

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Service Management Commands:"
echo "  View Django logs:      sudo tail -f $LOG_DIR/gunicorn.log"
echo "  View Bot logs:         sudo tail -f $LOG_DIR/telegram_bot.log"
echo "  Restart Django:        sudo supervisorctl restart opportuni"
echo "  Restart Bot:           sudo supervisorctl restart opportuni_telegram_bot"
echo "  View all status:       sudo supervisorctl status"
