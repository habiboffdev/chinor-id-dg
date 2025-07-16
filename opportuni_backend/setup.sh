#!/bin/bash

# Opportuni Backend Setup Script
echo "🚀 Setting up Opportuni Backend..."

# Check Python version
echo "📋 Checking Python version..."
python --version

# Upgrade pip, setuptools, and wheel first
echo "⬆️  Upgrading build tools..."
pip install --upgrade pip setuptools wheel

# Install minimal requirements first
echo "📦 Installing minimal requirements..."
pip install -r requirements-minimal.txt

# If minimal installation succeeds, install additional packages
if [ $? -eq 0 ]; then
    echo "✅ Minimal requirements installed successfully"
    echo "📦 Installing additional packages..."
    
    # Install remaining packages one by one
    echo "Installing filtering and search..."
    pip install "django-filter>=23.0,<24.0"
    
    echo "Installing background tasks..."
    pip install "celery>=5.3.0,<6.0" "redis>=4.5.0,<6.0"
    
    echo "Installing real-time features..."
    pip install "channels>=4.0.0,<5.0" "channels-redis>=4.1.0,<5.0"
    
    echo "Installing development tools..."
    pip install "django-extensions>=3.2.0,<4.0"
    
    echo "Installing API documentation..."
    pip install "drf-spectacular>=0.26.0,<1.0"
    
    echo "Installing timezone handling..."
    pip install "pytz>=2023.3"
    
    echo "✅ All packages installed successfully!"
    
    # Setup environment file
    if [ ! -f .env ]; then
        echo "📝 Creating environment file..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your configuration"
    fi
    
    echo "🎉 Setup complete! Next steps:"
    echo "1. Edit .env file with your database settings"
    echo "2. Run: python manage.py migrate"
    echo "3. Run: python manage.py createsuperuser"
    echo "4. Run: python manage.py runserver"
    
else
    echo "❌ Minimal requirements installation failed"
    echo "This might be due to Python 3.13 compatibility issues"
    echo "Please try the alternative installation method"
fi
