#!/bin/bash

# Opportuni MVP Deployment Script for DigitalOcean
# Run this script on your DigitalOcean droplet

echo "🚀 Starting Opportuni MVP Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please run this script as the opportuni user, not as root"
    exit 1
fi

# Set variables
PROJECT_DIR="/home/opportuni/opportuni"
VENV_DIR="$PROJECT_DIR/venv"
BACKEND_DIR="$PROJECT_DIR/opportuni_backend"

print_status "Setting up Python virtual environment..."
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r $BACKEND_DIR/requirements.txt
pip install gunicorn psycopg2-binary

print_status "Setting up environment variables..."
if [ ! -f "$BACKEND_DIR/.env" ]; then
    print_warning ".env file not found. Please create it from .env.example"
    cp $BACKEND_DIR/.env.example $BACKEND_DIR/.env
    print_warning "Please edit $BACKEND_DIR/.env with your production values"
    exit 1
fi

print_status "Running database migrations..."
cd $BACKEND_DIR
python manage.py migrate --settings=opportuni.settings.production

print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=opportuni.settings.production

print_status "Creating superuser (if needed)..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@opportuni.com', 'changeme123')" | python manage.py shell --settings=opportuni.settings.production

print_status "Testing Django application..."
python manage.py check --settings=opportuni.settings.production

if [ $? -eq 0 ]; then
    print_status "✅ Django application is ready!"
else
    print_error "❌ Django application has errors. Please fix them before continuing."
    exit 1
fi

print_status "Deployment completed! Next steps:"
echo "1. Configure Nginx (see nginx.conf in deployment folder)"
echo "2. Setup Supervisor (see supervisor.conf in deployment folder)"  
echo "3. Configure SSL with Let's Encrypt"
echo "4. Test your application"

print_status "🎉 Opportuni MVP is ready for production!"
