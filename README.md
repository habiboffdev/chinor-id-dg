	# Opportuni - Backend API

Django REST API for student-organization opportunity matching platform. Connects students with internships, scholarships, and opportunities while providing organizations with application management tools.

## 🏗️ Tech Stack

- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (simplejwt)
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Telegram Bot**: pyTelegramBotAPI
- **Deployment**: Gunicorn + Nginx + Supervisor

## 📁 Project Structure

```
opportuni_backend/
├── apps/
│   ├── accounts/         # Authentication & users
│   ├── students/         # Student profiles & data
│   ├── organizations/    # Organization management
│   ├── opportunities/    # Job/internship listings
│   ├── applications/     # Application workflow
│   ├── communications/   # Messaging system
│   ├── notifications/    # Real-time notifications
│   └── core/            # Shared utilities
├── opportuni/
│   └── settings/        # Environment configs
├── media/               # Uploaded files (dev)
├── mediafiles/          # Uploaded files (prod)
└── logs/               # Application logs

telegram_bot/
├── handlers/           # Bot command handlers
├── bot.py             # Entry points
└── config.py          # Django integration

deployment/
├── nginx.conf         # Web server config
├── supervisor.conf    # Process management
└── deploy.sh          # Deployment script
```

## 🚀 Quick Start

### Development Setup

```bash
# Clone repository
git clone https://github.com/habiboffdev/chinor-id-dg.git
cd chinor-id-dg/opportuni_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables

Create `.env` file in `opportuni_backend/`:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=opportuni_db
DB_USER=opportuni_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHANNEL_ID=your-channel-id
```

## 📊 API Documentation

**Interactive docs**: http://localhost:8000/api/docs/

### Key Endpoints

**Authentication**
- `POST /api/auth/register/` - User registration (student/organization)
- `POST /api/auth/login/` - Login (returns JWT)
- `POST /api/auth/token/refresh/` - Refresh access token

**Students**
- `GET/PUT /api/students/profile/` - Student profile
- `POST /api/students/upload-profile-picture/` - Avatar upload
- `GET /api/students/education/` - Education history

**Organizations**
- `GET/PUT /api/organizations/profile/` - Organization profile
- `POST /api/organizations/upload-logo/` - Logo upload
- `GET /api/organizations/dashboard/` - Dashboard stats

**Opportunities**
- `GET /api/opportunities/` - List opportunities
- `POST /api/opportunities/` - Create opportunity (org only)
- `GET /api/opportunities/{id}/` - Opportunity details

**Applications**
- `POST /api/applications/` - Submit application
- `GET /api/applications/` - List applications
- `PUT /api/applications/{id}/status/` - Update status (org only)

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts

# Check for issues
python manage.py check
```

## 🚢 Production Deployment

### Requirements
- Ubuntu 22.04+
- PostgreSQL 12+
- Nginx
- Supervisor

### Deploy Steps

```bash
# On production server
cd /home/chinor-id-dg/chinor_id_new

# Pull latest changes
git pull origin main

# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r opportuni_backend/requirements.txt

# Run migrations
cd opportuni_backend
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo supervisorctl restart opportuni
sudo systemctl reload nginx
```

### Media Files

Ensure media directories exist:
```bash
mkdir -p mediafiles/{avatars,org_logos,resumes,opportunity_covers,application_docs}
chmod -R 755 mediafiles/
```

## Telegram Bot

Separate virtual environment for bot dependencies:

```bash
# Create bot environment
python3 -m venv .venv_bot
source .venv_bot/bin/activate
pip install -r telegram_bot/requirements.txt

# Run bot (managed by supervisor in production)
python -c "from telegram_bot.bot import run_polling; run_polling()"
```

## Key Features

- **Dual User Types**: Students and organizations with separate interfaces
- **JWT Authentication**: Secure token-based auth with refresh
- **File Uploads**: Avatar, logo, resume, document handling
- **Telegram Integration**: Bot for channel administration and notifications
- **Organization Scoped Data**: Organizations only see their own data
- **Application Workflow**: Submit, review, accept/reject applications
- **OpenAPI Schema**: Auto-generated API documentation

## Security

- CORS configuration for frontend integration
- File upload validation (type, size)
- Organization data scoping
- JWT token blacklisting on logout
- HTTPS enforcement (production)

## Support

For issues or questions, refer to inline documentation or check application logs:
```bash
tail -f /home/chinor-id-dg/chinor_id_new/opportuni_backend/logs/django.log
```

---

**Note**: Frontend is a separate React application deployed independently.
