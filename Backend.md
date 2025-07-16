# Student Opportunity Management Platform - Django Backend
## Django + Django REST Framework Implementation

Build a comprehensive backend API for the Student Opportunity Management Platform "Opportuni" using Django, Django REST Framework, and multiple Django apps for modular architecture.

## 🏗️ Technical Stack

**Core Technologies:**
- **Django 4.2+** - Main web framework
- **Django REST Framework (DRF)** - API development
- **PostgreSQL** - Primary database
- **Django Channels** - WebSocket support for real-time notifications
- **Celery + Redis** - Background tasks and caching
- **Django Storages + AWS S3** - File storage
- **Django CORS Headers** - Frontend integration
- **JWT Authentication** - Token-based auth

**Additional Packages:**
```bash
pip install django djangorestframework
pip install psycopg2-binary  # PostgreSQL adapter
pip install django-cors-headers
pip install djangorestframework-simplejwt
pip install django-filter
pip install django-storages boto3  # AWS S3
pip install celery redis
pip install channels channels-redis
pip install pillow  # Image processing
pip install django-extensions
pip install python-decouple  # Environment variables
```

## 📁 Project Structure

```
opportuni_backend/
├── manage.py
├── requirements.txt
├── .env
├── opportuni/  # Main project
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py  # For Channels
│   └── celery.py
├── apps/
│   ├── __init__.py
│   ├── accounts/  # User management
│   ├── students/  # Student profiles and data
│   ├── organizations/  # Organization management
│   ├── opportunities/  # Events/opportunities
│   ├── applications/  # Application management
│   ├── communications/  # Email templates and messaging
│   ├── notifications/  # Real-time notifications
│   └── core/  # Shared utilities
├── static/
├── media/
├── templates/
└── tests/
```

## 🔧 Django Apps Architecture

### 1. **accounts/** - Authentication & User Management

**Models:**
```python
# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('organization', 'Organization'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
```

**API Endpoints:**
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (JWT)
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - Logout
- `GET/PUT /api/auth/profile/` - User profile
- `POST /api/auth/change-password/` - Password change
- `POST /api/auth/reset-password/` - Password reset

### 2. **students/** - Student Data Management

**Models:**
```python
# apps/students/models.py
from django.db import models
from apps.accounts.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    university = models.CharField(max_length=200)
    major = models.CharField(max_length=100)
    graduation_year = models.IntegerField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True)
    portfolio_url = models.URLField(blank=True)
    
class Education(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

class Experience(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50)

class StudentSkill(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.IntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced')])

class Project(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.ManyToManyField(Skill)
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

class Achievement(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_achieved = models.DateField()
    certificate = models.FileField(upload_to='certificates/', blank=True)
```

**API Endpoints:**
- `GET/PUT /api/students/profile/` - Student profile management
- `GET/POST /api/students/education/` - Education history
- `GET/POST /api/students/experience/` - Work experience
- `GET/POST /api/students/projects/` - Project portfolio
- `GET/POST /api/students/skills/` - Skills management
- `GET/POST /api/students/achievements/` - Achievements
- `POST /api/students/upload-resume/` - Resume upload
- `GET /api/students/dashboard-stats/` - Dashboard statistics

### 3. **organizations/** - Organization Management

**Models:**
```python
# apps/organizations/models.py
from django.db import models
from apps.accounts.models import User

class Organization(models.Model):
    ORGANIZATION_TYPES = (
        ('education', 'Education'),
        ('volunteering', 'Volunteering'),
        ('competition', 'Competition'),
        ('scholarship', 'Scholarship'),
        ('nonprofit', 'Non-profit'),
        ('government', 'Government'),
        ('corporation', 'Corporation'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES)
    description = models.TextField()
    logo = models.ImageField(upload_to='org_logos/', blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    
    # Location
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    
    # Social Media
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OrganizationMember(models.Model):
    ROLES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('recruiter', 'Recruiter'),
        ('viewer', 'Viewer'),
    )
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)
```

**API Endpoints:**
- `GET/PUT /api/organizations/profile/` - Organization profile
- `POST /api/organizations/upload-logo/` - Logo upload
- `GET /api/organizations/members/` - Team members
- `POST /api/organizations/invite-member/` - Invite team member
- `GET /api/organizations/dashboard-stats/` - Dashboard statistics
- `GET /api/organizations/search/` - Search organizations

### 4. **opportunities/** - Events & Opportunities Management

**Models:**
```python
# apps/opportunities/models.py
from django.db import models
from apps.organizations.models import Organization

class Opportunity(models.Model):
    OPPORTUNITY_TYPES = (
        ('internship', 'Internship'),
        ('volunteer', 'Volunteer'),
        ('competition', 'Competition'),
        ('scholarship', 'Scholarship'),
        ('job', 'Job'),
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=200)
    description = models.TextField()
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    application_deadline = models.DateTimeField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Requirements
    required_skills = models.ManyToManyField('students.Skill', blank=True)
    min_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    required_major = models.CharField(max_length=100, blank=True)
    graduation_year_min = models.IntegerField(null=True, blank=True)
    graduation_year_max = models.IntegerField(null=True, blank=True)
    
    # Details
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    compensation = models.CharField(max_length=100, blank=True)
    benefits = models.TextField(blank=True)
    
    # Meta
    max_applications = models.IntegerField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OpportunityRequirement(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='requirements')
    requirement = models.CharField(max_length=200)
    is_mandatory = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
```

**API Endpoints:**
- `GET /api/opportunities/` - List opportunities (with filtering)
- `POST /api/opportunities/` - Create opportunity
- `GET/PUT/DELETE /api/opportunities/{id}/` - Opportunity CRUD
- `GET /api/opportunities/search/` - Advanced search
- `POST /api/opportunities/{id}/publish/` - Publish opportunity
- `GET /api/opportunities/categories/` - Get categories
- `GET /api/opportunities/featured/` - Featured opportunities

### 5. **applications/** - Application Management

**Models:**
```python
# apps/applications/models.py
from django.db import models
from apps.students.models import StudentProfile
from apps.opportunities.models import Opportunity

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Application Data
    cover_letter = models.TextField()
    additional_documents = models.JSONField(default=list)  # Store file URLs
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Review Data
    reviewer_notes = models.TextField(blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('student', 'opportunity')

class ApplicationDocument(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='application_docs/')
    document_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ApplicationNote(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    note = models.TextField()
    is_internal = models.BooleanField(default=True)  # Internal org notes vs student-visible
    created_at = models.DateTimeField(auto_now_add=True)
```

**API Endpoints:**
- `POST /api/applications/` - Submit application
- `GET /api/applications/` - List applications (filtered by user)
- `GET/PUT /api/applications/{id}/` - Application details/update
- `POST /api/applications/{id}/withdraw/` - Withdraw application
- `PUT /api/applications/{id}/status/` - Update status (org only)
- `POST /api/applications/{id}/notes/` - Add note
- `GET /api/applications/{id}/documents/` - Application documents
- `POST /api/applications/bulk-update/` - Bulk status update

### 6. **communications/** - Email & Messaging

**Models:**
```python
# apps/communications/models.py
from django.db import models
from apps.organizations.models import Organization
from apps.accounts.models import User

class EmailTemplate(models.Model):
    TEMPLATE_TYPES = (
        ('application_received', 'Application Received'),
        ('interview_invitation', 'Interview Invitation'),
        ('acceptance_letter', 'Acceptance Letter'),
        ('rejection_letter', 'Rejection Letter'),
        ('reminder', 'Reminder'),
        ('custom', 'Custom'),
    )
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='email_templates')
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    variables = models.JSONField(default=list)  # Available template variables
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
class BulkEmail(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    recipients = models.JSONField()  # List of recipient IDs
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_count = models.IntegerField(default=0)
```

**API Endpoints:**
- `GET/POST /api/communications/templates/` - Email templates
- `GET/PUT/DELETE /api/communications/templates/{id}/` - Template CRUD
- `POST /api/communications/send-email/` - Send individual email
- `POST /api/communications/send-bulk/` - Send bulk email
- `GET /api/communications/messages/` - User messages
- `POST /api/communications/messages/` - Send message
- `PUT /api/communications/messages/{id}/read/` - Mark as read

### 7. **notifications/** - Real-time Notifications

**Models:**
```python
# apps/notifications/models.py
from django.db import models
from apps.accounts.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('application_status', 'Application Status Update'),
        ('new_opportunity', 'New Opportunity'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('message_received', 'Message Received'),
        ('interview_scheduled', 'Interview Scheduled'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)  # Additional notification data
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    application_updates = models.BooleanField(default=True)
    new_opportunities = models.BooleanField(default=True)
    deadline_reminders = models.BooleanField(default=True)
    messages = models.BooleanField(default=True)
```

**WebSocket Consumers:**
```python
# apps/notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"notifications_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))
```

**API Endpoints:**
- `GET /api/notifications/` - User notifications
- `PUT /api/notifications/{id}/read/` - Mark notification as read
- `PUT /api/notifications/mark-all-read/` - Mark all as read
- `GET/PUT /api/notifications/settings/` - Notification preferences
- `DELETE /api/notifications/{id}/` - Delete notification

### 8. **core/** - Shared Utilities

**Utilities:**
```python
# apps/core/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsOrganizationMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'organization'

# apps/core/pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# apps/core/filters.py
import django_filters
from apps.opportunities.models import Opportunity

class OpportunityFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    opportunity_type = django_filters.MultipleChoiceFilter(choices=Opportunity.OPPORTUNITY_TYPES)
    min_gpa = django_filters.NumberFilter(field_name='min_gpa', lookup_expr='lte')
    
    class Meta:
        model = Opportunity
        fields = ['title', 'location', 'opportunity_type', 'is_remote']
```

## 🔒 Authentication & Permissions

**JWT Configuration:**
```python
# settings/base.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsSetPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

## 🚀 Celery Tasks

**Background Tasks:**
```python
# apps/core/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from apps.notifications.models import Notification

@shared_task
def send_email_notification(user_id, subject, message):
    # Send email notification
    pass

@shared_task
def send_bulk_emails(template_id, recipient_ids):
    # Send bulk emails
    pass

@shared_task
def deadline_reminder_task():
    # Check for upcoming deadlines and send reminders
    pass

@shared_task
def cleanup_old_notifications():
    # Clean up old notifications
    pass
```

## 📊 API Documentation

**Key API Features:**
- **Filtering & Search:** All list endpoints support filtering, searching, and ordering
- **Pagination:** Standard pagination for all list endpoints
- **File Uploads:** Support for resume, documents, images
- **Bulk Operations:** Bulk status updates, bulk emails
- **Real-time Updates:** WebSocket notifications
- **Email Integration:** Automated email sending
- **Data Export:** CSV/PDF export capabilities

## 🔧 Advanced Features

1. **Analytics Dashboard:**
   - Application conversion rates
   - Popular opportunities
   - Student engagement metrics
   - Organization performance

2. **Matching Algorithm:**
   - AI-powered opportunity matching
   - Skill-based recommendations
   - Success prediction scoring

3. **Reporting System:**
   - Custom reports for organizations
   - Student progress tracking
   - Platform usage analytics

4. **Integration APIs:**
   - University system integration
   - LinkedIn profile import
   - Calendar integration for interviews

This comprehensive Django backend provides all the functionality needed for your Student Opportunity Management Platform with proper separation of concerns, scalable architecture, and modern API design patterns.