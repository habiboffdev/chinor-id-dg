# Copilot Instructions for Opportuni MVP

## Project Overview
This is a Django REST API backend with vanilla HTML/CSS/JS frontend for a student-organization opportunity matching platform. The system connects students with internship/scholarship opportunities from organizations, with integrated Telegram bot for channel administration and user engagement.

## Architecture
- **Backend**: Django REST Framework with JWT authentication
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks, no Tailwind)
- **Database**: PostgreSQL (production), SQLite (development)
- **Telegram Bot**: pyTelegramBotAPI with dedicated virtual environment
- **Deployment**: Gunicorn + Nginx + Supervisor for multi-service management

## Brand & Design System
- **Fonts**: Space Grotesk (display), Inter (body)
- **Colors**: Dark-first palette with accent tokens (--accent-1, --accent-2)
- **CSS Architecture**: Semantic classes only, NO utility classes or Tailwind
- **Theme**: All pages must use `body.theme-opportuni` wrapper
- **Universal Components**: Shared navbar, consistent button/card styles

## Key Principles
1. **Brand-First Design**: Strict adherence to BRAND_BLUEPRINT.md rules
2. **No Tailwind**: Use semantic CSS classes and brand tokens only
3. **Universal Components**: Reusable navbar, consistent styling across pages
4. **Django Best Practices**: Use built-in features, follow REST conventions
5. **Clear Separation**: Distinct student vs organization interfaces

## Backend Structure

### Django Apps
- **accounts**: User authentication, profiles, JWT tokens
- **students**: Student profiles, education, experience, skills, projects
- **organizations**: Organization profiles, dashboard, members
- **opportunities**: Job/internship listings, requirements, questions
- **applications**: Student applications to opportunities
- **communications**: Messaging, email templates, notifications
- **notifications**: Real-time notifications, settings
- **core**: Shared utilities, pagination, permissions, tasks

### API Patterns
- Use Django REST Framework ViewSets and generic views
- JWT authentication via rest_framework_simplejwt
- Standard serializers for CRUD operations
- Separate serializers for list/detail/create/update operations
- Filtering with django-filter, search with DRF SearchFilter
- Custom pagination class in core.pagination
- Permission classes for organization-scoped data

### Model Relationships
- User → StudentProfile/Organization (OneToOne via user_type field)
- Organization → Opportunity (ForeignKey)
- Student → Application → Opportunity (through relationship)
- Opportunity → OpportunityRequirement/OpportunityQuestion (reverse FK)
- Student → Education/Experience/Skill/Project (reverse FK)

### URL Structure
```
/api/auth/ - Authentication endpoints
/api/students/ - Student profiles and related data
/api/organizations/ - Organization profiles and dashboard
/api/opportunities/ - Opportunity listings and CRUD
/api/applications/ - Application management
/api/communications/ - Messaging system
/api/notifications/ - Notification management
```

## Frontend Structure

### Page Architecture
- **Student Pages**: `/` (landing), `/dashboard.html`, `/opportunities.html`, `/applications.html`, `/profile.html`
- **Organization Pages**: `/organization/` folder with dashboard, opportunities, applications, students, communications, profile
- **Shared Components**: Universal navbars, authentication forms

### JavaScript Architecture
- **auth.js**: Authentication manager, user sessions, redirects
- **api.js**: API client with organized endpoints by domain
- **main.js**: Page-specific controllers and utilities
- **components.js**: Reusable UI components (modals, forms, etc.)
- **navbar.js**: Student navbar controller
- **org-navbar.js**: Organization navbar controller

### CSS Architecture
- **theme.css**: Brand tokens, typography, base styles
- **styles.css**: General component styles
- **org.css**: Organization-specific components
- **layout-shim.css**: Minimal utility classes for layout

### Navbar Requirements
- **Student Navbar**: Rendered by navbar.js into `#student-navbar-root`
- **Organization Navbar**: Rendered by org-navbar.js, mount with `OrgNavbar.mount()`
- Both navbars: Sticky positioning, dropdown menus, active states, responsive design
- Required scripts: Include respective navbar JS and call mount functions

## Development Workflows

### Backend Development
1. **Model Changes**: Create migrations with `python manage.py makemigrations`
2. **API Testing**: Use Django shell or curl for endpoint testing
3. **System Checks**: Run `python manage.py check` before commits
4. **Permissions**: Always check user permissions in views (student vs org data)
5. **Telegram Bot**: Use dedicated `.venv_bot` environment and management commands

### Frontend Development
1. **Local Server**: `cd opportuni_frontend && python3 -m http.server 8080`
2. **Page Structure**: Always include theme.css, relevant navbar, brand wrapper
3. **Script Loading**: Load dependencies in order: utils → api → auth → components → page-specific
4. **API Integration**: Use api.js client methods, handle errors gracefully

### Telegram Bot Development
1. **Environment**: Always use `.venv_bot` virtual environment
2. **Django Integration**: Use `setup_django()` for ORM access
3. **Testing**: Use management commands with `--mock-bot` flag for safe testing
4. **Channel Setup**: Configure bot as channel admin with posting permissions

### Organization Pages Checklist
- [ ] Include theme.css, org.css, layout-shim.css
- [ ] Add `<div id="org-navbar"></div>` at top of body
- [ ] Include org-navbar.js and call `OrgNavbar.mount()`
- [ ] Wrap with `body.theme-opportuni`
- [ ] Use semantic CSS classes only (no utilities)
- [ ] Test navbar dropdown functionality
- [ ] Verify active page highlighting

### API Client Usage
```javascript
// Get organization dashboard data
const dashboard = await api.organizations.dashboard();

// List applications for organization
const apps = await api.applications.listForOrg();

// Create new opportunity
const opportunity = await api.opportunities.create(data);
```

## Telegram Bot Integration

### Architecture & Environment Setup
- **Isolated Environment**: Bot runs in dedicated `.venv_bot` virtual environment
- **Django Integration**: Uses `setup_django()` for ORM access and Django management commands
- **Channel Administration**: Automatic opportunity posting to Telegram channels
- **Multi-service Deployment**: Managed via Supervisor alongside Django app

### Key Bot Components
- **config.py**: Environment loading, TeleBot instance, Django setup
- **handlers/**: Modular command handlers (student, admin, common)
- **bot.py**: Main entry point with `run_polling()` and `run_webhook()`
- **markups.py**: Telegram keyboards and inline buttons
- **i18n.py**: Multi-language support (en/ru/uz)

### Django Integration Patterns
```python
# Django management commands for bot operations
python manage.py run_telegram_bot  # Run bot from Django
python manage.py test_telegram_channel --latest  # Test channel posting
python manage.py test_telegram_posting --mock-bot  # Test with mocks

# Bot configuration in Django settings
TELEGRAM_BOT_TOKEN = config('BOT_TOKEN')
TELEGRAM_CHANNEL_ID = config('TELEGRAM_CHANNEL_ID')
TELEGRAM_ADMIN_IDS = config('TELEGRAM_ADMIN_IDS', default='').split(',')
```

### Environment Management
```bash
# Bot environment setup (from project root)
python3 -m venv .venv_bot
source .venv_bot/bin/activate
pip install -r telegram_bot/requirements.txt

# Django environment (separate)
cd opportuni_backend
source venv/bin/activate  # or ../venv/bin/activate
```

## Common Pitfalls

### Backend
- Don't forget organization scoping in views (filter by request.user's org)
- Use get_or_create for student profiles to handle missing records
- Separate serializers for different operations (list vs detail vs create)
- Always include permission checks in custom views

### Frontend
- Never use Tailwind classes - use semantic CSS only
- Include all required scripts in correct order
- Mount navbars explicitly with JavaScript
- Test dropdown menus on mobile devices
- Verify API endpoints match backend URLs exactly

### Telegram Bot Development
- Always switch to `.venv_bot` environment before bot work
- Use `setup_django()` in bot code to access Django ORM
- Test with `--mock-bot` flag to avoid hitting Telegram API during development
- Keep bot and Django environments separate to avoid dependency conflicts

### Brand Compliance
- Use Space Grotesk for headings, Inter for body text
- Follow dark-first color palette from theme.css
- No utility classes - semantic component classes only
- Consistent button, card, and form styling across all pages

## File Organization
```
opportuni_backend/
├── apps/
│   ├── accounts/          # User auth and profiles
│   ├── students/          # Student data and dashboard
│   ├── organizations/     # Organization data and dashboard
│   ├── opportunities/     # Job/internship listings
│   ├── applications/      # Application management
│   ├── communications/    # Messaging system
│   └── notifications/     # Real-time notifications
├── opportuni/settings/    # Environment-specific settings
└── static/media/         # Static and uploaded files

opportuni_frontend/
├── assets/
│   ├── css/              # Brand and component styles
│   └── js/               # API client and controllers
├── organization/         # Organization-specific pages
└── *.html               # Student-facing pages

telegram_bot/
├── handlers/             # Modular command handlers
├── config.py             # Environment & Django setup
├── bot.py                # Entry points (polling/webhook)
├── markups.py            # Keyboards and buttons
└── i18n.py               # Multi-language support
```

This structure ensures maintainable, scalable code that follows Django and frontend best practices while maintaining strict brand consistency.
