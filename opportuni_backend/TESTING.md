# Backend Testing Guide

## Overview

This document provides comprehensive testing guidelines for the Opportuni backend systems. The test suite covers all major backend components including notifications, application management, communications, and system integrations.

## Test Structure

```
opportuni_backend/
├── apps/
│   ├── notifications/tests.py      # Notification system tests
│   ├── applications/tests.py       # Application management tests
│   ├── communications/tests.py     # Communications system tests
│   └── core/tests_integration.py   # Cross-system integration tests
├── run_tests.sh                    # Test runner script
└── TESTING.md                      # This documentation
```

## Test Categories

### 1. Notification System Tests (`apps/notifications/tests.py`)

**Coverage:**
- ✅ Model functionality and validation
- ✅ Serializer data transformation
- ✅ API endpoint security and permissions
- ✅ Student and organization workflows
- ✅ Notification settings and preferences
- ✅ Bulk operations and cleanup

**Key Test Classes:**
- `NotificationModelTest` - Model validation and behavior
- `NotificationSettingsModelTest` - User preference management
- `NotificationSerializerTest` - Data serialization
- `NotificationAPITest` - API endpoint functionality
- `NotificationSettingsAPITest` - Settings management API
- `NotificationWorkflowTest` - User-specific workflows
- `NotificationIntegrationTest` - Cross-system integration

### 2. Application Management Tests (`apps/applications/tests.py`)

**Coverage:**
- ✅ Application lifecycle management
- ✅ Status change workflows
- ✅ Permission and access control
- ✅ Student-organization interactions
- ✅ Document and note management
- ✅ Question-answer system

**Key Test Classes:**
- `ApplicationModelTest` - Core application functionality
- `ApplicationDocumentModelTest` - File attachment handling
- `ApplicationNoteModelTest` - Note and review system
- `ApplicationSerializerTest` - Data transformation
- `ApplicationAPITest` - API endpoints and CRUD operations
- `ApplicationWorkflowTest` - Status progression workflows
- `ApplicationPermissionTest` - Access control and isolation

### 3. Communications System Tests (`apps/communications/tests.py`)

**Coverage:**
- ✅ Message system functionality
- ✅ Email template management
- ✅ Bulk communication operations
- ✅ Student-organization messaging
- ✅ Template-based communications
- ✅ Integration with applications

**Key Test Classes:**
- `EmailTemplateModelTest` - Template creation and management
- `MessageModelTest` - Message functionality
- `MessageThreadModelTest` - Conversation threading
- `CommunicationsSerializerTest` - Data serialization
- `CommunicationsAPITest` - API endpoints
- `BulkEmailTest` - Mass communication features
- `CommunicationsWorkflowTest` - User interaction workflows
- `CommunicationsIntegrationTest` - System integration

### 4. Integration Tests (`apps/core/tests_integration.py`)

**Coverage:**
- ✅ Complete user workflows
- ✅ Cross-system permissions
- ✅ Data consistency across systems
- ✅ Performance and scalability aspects
- ✅ Student-organization interaction patterns

**Key Test Classes:**
- `StudentOrganizationWorkflowTest` - End-to-end workflows
- `CrossSystemPermissionsTest` - Permission isolation
- `SystemIntegrationTest` - Data consistency
- `NotificationSystemIntegrationTest` - Notification integration
- `PerformanceAndScalabilityTest` - Performance considerations

## Running Tests

### Quick Start

```bash
# Navigate to backend directory
cd opportuni_backend

# Activate virtual environment (if not already active)
source ../venv/bin/activate  # or source venv/bin/activate

# Run all tests
./run_tests.sh

# Run specific test suite
./run_tests.sh notifications
./run_tests.sh applications
./run_tests.sh communications
./run_tests.sh integration

# Run with coverage analysis
./run_tests.sh coverage
```

### Manual Test Execution

```bash
# Run specific app tests
python manage.py test apps.notifications.tests --verbosity=2
python manage.py test apps.applications.tests --verbosity=2
python manage.py test apps.communications.tests --verbosity=2
python manage.py test apps.core.tests_integration --verbosity=2

# Run all tests with coverage
coverage run --source='apps' manage.py test
coverage report --show-missing
coverage html
```

### Test Database Setup

Tests automatically create and tear down test databases. Ensure your settings include:

```python
# settings/base.py or settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for tests
    }
}
```

## Test Scenarios Covered

### Student Workflows
- ✅ Student registration and profile creation
- ✅ Application submission with documents and answers
- ✅ Application status tracking
- ✅ Receiving and reading notifications
- ✅ Messaging with organizations
- ✅ Managing notification preferences

### Organization Workflows
- ✅ Organization profile management
- ✅ Opportunity creation and management
- ✅ Application review and status updates
- ✅ Student communication
- ✅ Email template creation and usage
- ✅ Bulk communication operations

### System Integration
- ✅ Application status changes trigger notifications
- ✅ Messages link to specific applications
- ✅ Email templates integrate with messaging
- ✅ Permission isolation between users
- ✅ Data consistency across operations

### Security and Permissions
- ✅ Students only see their own applications
- ✅ Organizations only see applications for their opportunities
- ✅ Message access restricted to participants
- ✅ Notification isolation between users
- ✅ API endpoint authentication requirements

## Test Data Patterns

### User Creation Pattern
```python
student_user = User.objects.create_user(
    username='student',
    email='student@example.com',
    password='testpass123',
    user_type='student'
)
Profile.objects.create(user=student_user)
student_profile = StudentProfile.objects.create(
    user=student_user,
    university='Test University',
    field_of_study='Computer Science'
)
```

### Organization Setup Pattern
```python
org_user = User.objects.create_user(
    username='orguser',
    email='org@example.com',
    password='testpass123',
    user_type='organization'
)
Profile.objects.create(user=org_user)
organization = Organization.objects.create(
    user=org_user,
    name='Test Organization',
    organization_type='private_company',
    description='Test organization',
    website='https://test.com',
    location='Test City'
)
```

### API Testing Pattern
```python
self.client = APIClient()
self.client.force_authenticate(user=self.student_user)
response = self.client.get(reverse('endpoint-name'))
self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Performance Considerations

### Database Optimization
- Use `select_related()` and `prefetch_related()` for related data
- Test query count with `django.test.utils.override_settings(DEBUG=True)`
- Verify bulk operations for large datasets

### Test Performance
- Use `TransactionTestCase` for tests requiring database transactions
- Mock external services (email, file uploads) to speed up tests
- Use factory patterns for creating test data

## Continuous Integration

### GitHub Actions Example
```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd opportuni_backend
          python manage.py test apps.notifications.tests apps.applications.tests apps.communications.tests apps.core.tests_integration
```

## Coverage Goals

| Component | Current Coverage | Target Coverage |
|-----------|------------------|-----------------|
| Notifications | 95%+ | 98% |
| Applications | 95%+ | 98% |
| Communications | 95%+ | 98% |
| Integration | 90%+ | 95% |

## Common Issues and Solutions

### Test Database Issues
```bash
# Clear test database cache
python manage.py flush --verbosity=0
python manage.py migrate --run-syncdb
```

### Import Errors
```bash
# Ensure Python path includes project root
export PYTHONPATH="/path/to/opportuni_backend:$PYTHONPATH"
```

### Mock Configuration
```python
# Mock external services
@patch('apps.communications.views.send_mail')
def test_email_sending(self, mock_send_mail):
    mock_send_mail.return_value = True
    # Test logic here
```

## Adding New Tests

### 1. Model Tests
```python
class NewModelTest(TestCase):
    def setUp(self):
        # Create test data
        pass
    
    def test_model_creation(self):
        # Test model creation and validation
        pass
    
    def test_model_methods(self):
        # Test custom model methods
        pass
```

### 2. API Tests
```python
class NewAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users and data
        pass
    
    def test_list_endpoint(self):
        # Test GET requests
        pass
    
    def test_create_endpoint(self):
        # Test POST requests
        pass
    
    def test_permissions(self):
        # Test access control
        pass
```

### 3. Integration Tests
```python
class NewIntegrationTest(TransactionTestCase):
    def test_workflow(self):
        # Test complete user workflows
        pass
    
    def test_cross_system_interaction(self):
        # Test interactions between systems
        pass
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Clarity**: Test names should clearly describe what is being tested
3. **Coverage**: Aim for high test coverage, especially for critical paths
4. **Performance**: Keep tests fast by mocking external dependencies
5. **Maintainability**: Use helper methods and factories for common setup
6. **Documentation**: Document complex test scenarios and expected behaviors

## Troubleshooting

### Common Test Failures

1. **Permission Denied**: Ensure proper user authentication in API tests
2. **Database Integrity**: Check for unique constraint violations in test data
3. **Import Errors**: Verify Python path and module imports
4. **Timing Issues**: Use proper timezone handling for datetime comparisons
5. **Mock Issues**: Ensure mocks are properly configured and cleaned up

### Debugging Tips

```python
# Add debug output
import pdb; pdb.set_trace()

# Print query count
from django.db import connection
print(f"Queries executed: {len(connection.queries)}")

# Check test database state
python manage.py dbshell --settings=myproject.settings.test
```

## Future Enhancements

1. **Automated Performance Testing**: Add performance benchmarks
2. **Load Testing**: Test system behavior under load
3. **Security Testing**: Add security-focused test scenarios
4. **Browser Testing**: Add Selenium tests for frontend integration
5. **API Documentation Testing**: Validate API documentation accuracy