# Development Setup Guide

## Step 1: Backend Setup

### 1.1 Install Python and Create Virtual Environment
```bash
# Navigate to backend directory
cd opportuni_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 1.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.3 Setup Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

Required environment variables:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=opportuni_db
DB_USER=opportuni_user
DB_PASSWORD=your-password-here
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 1.4 Setup PostgreSQL Database

First, ensure PostgreSQL is installed and running:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# If not running, start it
sudo systemctl start postgresql

# If not installed (Ubuntu/Debian):
sudo apt update && sudo apt install postgresql postgresql-contrib
```

Connect to PostgreSQL and create database:
```bash
# Connect as postgres superuser
sudo -u postgres psql
```

In the PostgreSQL prompt, run:
```sql
-- Create database and user
CREATE DATABASE opportuni_db;
CREATE USER opportuni_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE opportuni_db TO opportuni_user;
ALTER USER opportuni_user CREATEDB;

-- Exit PostgreSQL
\q
```

Test the connection:
```bash
# Test connection with new user
psql -U opportuni_user -d opportuni_db -h localhost
```

### 1.5 Run Database Migrations

First, ensure all required directories exist:
```bash
# Create missing directories
mkdir -p logs static media templates
```

Create migrations and apply them:
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

**If you get permission errors**, fix PostgreSQL permissions:
```bash
# Grant necessary privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE opportuni_db TO opportuni_user;"
sudo -u postgres psql opportuni_db -c "GRANT ALL ON SCHEMA public TO opportuni_user;"
sudo -u postgres psql opportuni_db -c "GRANT USAGE, CREATE ON SCHEMA public TO opportuni_user;"

# Then retry migrations
python manage.py migrate
```

Create a superuser:
```bash
python manage.py createsuperuser
```

### 1.6 Start Development Server
```bash
python manage.py runserver
```

### 1.7 Start Celery Worker (Optional - for background tasks)
```bash
# In a new terminal with activated virtual environment
celery -A opportuni worker --loglevel=info
```

## Step 2: Frontend Setup

### 2.1 Navigate to Frontend Directory
```bash
cd opportuni_frontend
```

### 2.2 Start Local Web Server
Option 1 - Using Python:
```bash
python -m http.server 8080
```

Option 2 - Using Node.js:
```bash
npx http-server -p 8080
```

Option 3 - Using PHP:
```bash
php -S localhost:8080
```

## Step 3: Access the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs

## Development Tools

### VS Code Extensions (Recommended)
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.black-formatter",
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-json"
    ]
}
```

### API Testing
Use these tools to test the API:
- **Postman**: Import API collection
- **curl**: Command line testing
- **DRF Browsable API**: Built-in interface

### Database Management
- **pgAdmin**: PostgreSQL GUI
- **psql**: Command line interface
- **Django Admin**: Built-in interface

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

2. **Database connection error**
   - Check PostgreSQL is running
   - Verify database credentials
   - Ensure database exists

3. **Redis connection error**
   ```bash
   # Start Redis server
   redis-server
   ```

4. **Static files not loading**
   ```bash
   python manage.py collectstatic
   ```

### Environment Setup Script
Create `setup.sh` for quick setup:
```bash
#!/bin/bash
echo "Setting up Opportuni development environment..."

# Backend setup
cd opportuni_backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

echo "Please edit .env file with your configuration"
echo "Then run: python manage.py migrate"
echo "And: python manage.py createsuperuser"
```

## Next Steps

1. **Create sample data**
   ```bash
   python manage.py loaddata sample_data.json
   ```

2. **Run tests**
   ```bash
   python manage.py test
   ```

3. **Start development**
   - Review the API documentation
   - Check existing models and serializers
   - Begin implementing features

Happy coding! 🚀
