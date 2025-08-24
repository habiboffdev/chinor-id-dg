# Opportuni - Student Opportunity Management Platform

## Project Overview
Opportuni connects students with internships, scholarships, competitions, and volunteer positions while providing organizations with tools to manage applications. The project is structured as:

- **Backend**: Django REST Framework with multiple specialized apps
- **Frontend**: Vanilla JavaScript (no frameworks) with HTML/CSS

## Architecture

### Backend (Django + DRF)
- **Core Framework**: Django 4.2+ with modular app structure
- **Database**: PostgreSQL with custom models
- **Authentication**: JWT token system
- **API**: REST endpoints across specialized apps
- **Async**: Django Channels for WebSockets (notifications)
- **Background Tasks**: Celery + Redis

### Frontend (Vanilla JavaScript)
- **Pure ES6+**: No frameworks or build tools
- **API Communication**: Custom fetch wrapper with token auth
- **State Management**: LocalStorage for persistence
- **Components**: Custom JavaScript components
- **Styling**: CSS Grid/Flexbox with custom properties

## Key Files & Directories

### Backend Structure
```
opportuni_backend/
├── manage.py                # Django management script
├── opportuni/               # Main Django project config
├── apps/                    # Django applications
│   ├── accounts/            # Authentication & users
│   ├── students/            # Student profiles
│   ├── organizations/       # Organization management
│   ├── opportunities/       # Listings & opportunities
│   ├── applications/        # Application handling
│   ├── communications/      # Messaging
│   └── notifications/       # Real-time notifications
```

### Frontend Structure
```
opportuni_frontend/
├── index.html               # Landing page
├── dashboard.html           # Student dashboard
├── opportunities.html       # Browse opportunities
├── profile.html             # Student profile
├── assets/
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript modules
│   │   ├── api.js           # API wrapper
│   │   ├── auth.js          # Authentication
│   │   ├── main.js          # Core functionality
│   │   └── utils.js         # Utilities
│   └── images/              # Static images
```

## Development Workflow

### Backend Development
1. **Run the server**: 
   ```bash
   cd opportuni_backend
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Make migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **API Structure**: Every Django app has its own serializers, viewsets, and URLs
   - Each app follows: models → serializers → views → urls pattern
   - Apps communicate through Django's ORM relationships

### Frontend Development
1. **Run local server**:
   ```bash
   cd opportuni_frontend
   python -m http.server 8080
   ```

2. **Authentication Flow**:
   - Login process is handled in `auth.js`
   - JWT tokens stored in localStorage
   - `requireAuth()` function used to protect pages

3. **API Integration**:
   - API calls use `api.js` wrapper
   - Endpoints organized by resource (students, opportunities, etc.)
   - Authentication headers automatically added to requests

## Key Patterns & Conventions

### Authentication
- Uses JWT tokens stored in localStorage
- Token refresh handled automatically in `auth.js`
- `isLoggedIn()` checks for valid token
- `requireAuth()` redirects unauthenticated users

### API Integration
- Frontend uses consistent pattern for API calls:
```javascript
// Example: api.opportunities.getAll() returns all opportunities
const opportunities = await api.opportunities.getAll();
```

### Data Handling
- Backend: Django REST Framework serializers enforce validation
- Frontend: Form validation using custom JavaScript functions
- ID patterns: `student_id`, `opportunity_id` used consistently

### State Management
- Data fetched from API and stored in variables/DOM
- Form state managed with JavaScript objects
- User state (auth) stored in localStorage

## Common Tasks

### Adding New Feature
1. Identify Django app for backend changes
2. Update/create models and run migrations
3. Create/modify serializers and viewsets
4. Update/create API endpoints in urls.py
5. Add frontend API calls in appropriate JavaScript file
6. Update UI to display and interact with the new data

### Fixing Authentication Issues
- Check for token validity in LocalStorage
- Verify JWT token expiration
- Review backend permissions in DRF viewsets
- Check CORS settings if cross-origin requests fail

### Database Migrations
- Recent fix: Made StudentProfile fields nullable to prevent constraint errors
- When changing models, be sure to create and apply migrations
- If you encounter NOT NULL constraint issues, may need raw SQL:
```sql
ALTER TABLE students_studentprofile ALTER COLUMN field_name DROP NOT NULL;
```

## Recent Fixes & Known Issues

### Fixed Issues
- Authentication flow now works correctly with token persistence
- StudentProfile NOT NULL constraints fixed with migration
- Profile update functionality fixed by handling user fields correctly

### Current Challenges
- File upload optimization needed for documents/images
- Form validation could be enhanced on frontend
- Additional error handling needed for edge cases

## Testing

### Backend Testing
```bash
python manage.py test
```

### Frontend Testing
- Manual testing of user flows
- Check console for errors
- Verify API responses with browser dev tools

## Deployment
Project uses a DigitalOcean Ubuntu server with:
- Nginx for serving static files and proxying
- Gunicorn for WSGI application server
- Supervisor for process management
- PostgreSQL for database

Deployment scripts in `deployment/` directory.
