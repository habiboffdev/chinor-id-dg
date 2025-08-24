# Opportuni - Student Opportunity Management Platform

## 📋 Project Overview

Opportuni is a comprehensive platform that connects students with opportunities such as internships, scholarships, competitions, and volunteer positions while providing organizations with powerful tools to manage applications and communicate with candidates.

## 🏗️ Architecture

### Backend (Django + DRF)
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **Real-time**: Django Channels + WebSockets
- **Background Tasks**: Celery + Redis
- **File Storage**: AWS S3 (production) / Local (development)

### Frontend (Vanilla JS)
- **Technologies**: HTML5, CSS3, ES6+ JavaScript
- **Styling**: CSS Grid, Flexbox, Custom Properties
- **No Dependencies**: Pure vanilla implementation
- **Responsive**: Mobile-first design

## 📁 Project Structure

```
opportuni_platform/
├── opportuni_backend/          # Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── opportuni/              # Main Django project
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py
│   └── apps/                   # Django applications
│       ├── accounts/           # User authentication
│       ├── students/           # Student profiles
│       ├── organizations/      # Organization management
│       ├── opportunities/      # Events and opportunities
│       ├── applications/       # Application management
│       ├── communications/     # Email and messaging
│       ├── notifications/      # Real-time notifications
│       └── core/               # Shared utilities
├── opportuni_frontend/         # Frontend application
│   ├── index.html              # Landing page
│   ├── dashboard.html          # Student dashboard
│   ├── profile.html            # Student profile
│   ├── opportunities.html      # Browse opportunities
│   ├── organization/           # Organization pages
│   ├── css/                    # Stylesheets
│   │   ├── styles.css
│   │   ├── components.css
│   │   └── responsive.css
│   ├── js/                     # JavaScript modules
│   │   ├── main.js
│   │   ├── auth.js
│   │   └── utils.js
│   └── assets/                 # Images and icons
└── docs/                       # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ (for development tools)
- PostgreSQL 12+
- Redis 6+

### Backend Setup

1. **Create virtual environment**
   ```bash
   cd opportuni_backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Setup database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

6. **Start Celery worker** (in separate terminal)
   ```bash
   celery -A opportuni worker --loglevel=info
   ```

### Frontend Setup

1. **Start local server**
   ```bash
   cd opportuni_frontend
   # Using Python's built-in server
   python -m http.server 8080
   # Or using Node.js
   npx http-server -p 8080
   ```

2. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/api/docs

## 🔧 Development Workflow

### Backend Development

1. **Create new Django app**
   ```bash
   python manage.py startapp app_name apps/app_name
   ```

2. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Run tests**
   ```bash
   python manage.py test
   ```

### Frontend Development

1. **File Structure**
   - Keep components modular
   - Use CSS custom properties for theming
   - Organize JavaScript into modules

2. **Styling Guidelines**
   - Mobile-first responsive design
   - Use semantic HTML
   - Follow BEM methodology for CSS classes

3. **JavaScript Guidelines**
   - Use ES6+ features
   - Keep functions pure when possible
   - Handle errors gracefully

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `GET/PUT /api/auth/profile/` - User profile

### Students
- `GET/PUT /api/students/profile/` - Student profile
- `GET/POST /api/students/education/` - Education history
- `GET/POST /api/students/experience/` - Work experience

### Organizations
- `GET/PUT /api/organizations/profile/` - Organization profile
- `GET /api/organizations/members/` - Team members

### Opportunities
- `GET /api/opportunities/` - List opportunities
- `POST /api/opportunities/` - Create opportunity
- `GET/PUT/DELETE /api/opportunities/{id}/` - Opportunity CRUD

### Applications
- `POST /api/applications/` - Submit application
- `GET /api/applications/` - List applications
- `PUT /api/applications/{id}/status/` - Update status

## 🎨 UI/UX Guidelines

### Design System
- **Primary Color**: #3b82f6 (Blue)
- **Secondary Color**: #10b981 (Green)
- **Success**: #10b981
- **Warning**: #f59e0b
- **Error**: #ef4444

### Typography
- **Font Family**: Inter, system fonts
- **Base Size**: 16px
- **Scale**: 0.75rem - 2.25rem

### Components
- Buttons with hover states
- Form validation feedback
- Modal dialogs
- Toast notifications
- Responsive tables
- Card layouts

## 🔐 Security Features

- JWT authentication with refresh tokens
- CORS configuration
- Input validation and sanitization
- File upload restrictions
- Rate limiting (production)
- HTTPS enforcement (production)

## 📈 Performance Optimization

### Backend
- Database query optimization
- Caching with Redis
- Background task processing
- File compression and CDN

### Frontend
- Lazy loading of images
- Minimized CSS/JS (production)
- Browser caching strategies
- Responsive image formats

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts

# Coverage report
coverage run --source='.' manage.py test
coverage report
```

### Frontend Testing
- Manual testing checklist
- Cross-browser compatibility
- Mobile device testing
- Accessibility testing

## 🚢 Deployment

### Backend Deployment
1. **Environment Configuration**
   ```bash
   export DJANGO_SETTINGS_MODULE=opportuni.settings.production
   ```

2. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate
   ```

### Frontend Deployment
1. **Build Optimization**
   - Minify CSS/JS files
   - Optimize images
   - Configure CDN

2. **Server Configuration**
   - NGINX/Apache setup
   - SSL certificate
   - Cache headers

## 📞 Support & Contributing

### Getting Help
- Check documentation first
- Search existing issues
- Create detailed bug reports

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

- **Backend Development**: Django REST Framework
- **Frontend Development**: Vanilla JavaScript
- **UI/UX Design**: Modern CSS
- **DevOps**: Docker, AWS, CI/CD

---

For more detailed information, please refer to the specific documentation in each module's directory.
