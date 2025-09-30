"""
Comprehensive unit tests for the Notifications system.
Tests cover models, serializers, views, and user workflows for both students and organizations.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from datetime import timedelta

from apps.notifications.models import Notification, NotificationSettings
from apps.notifications.serializers import NotificationSerializer, NotificationSettingsSerializer
from apps.accounts.models import Profile
from apps.students.models import StudentProfile
from apps.organizations.models import Organization

User = get_user_model()


class NotificationModelTest(TestCase):
    """Test Notification model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='student'
        )
        
    def test_notification_creation(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='application_status',
            title='Application Update',
            message='Your application has been reviewed',
            data={'application_id': 123}
        )
        
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.notification_type, 'application_status')
        self.assertEqual(notification.title, 'Application Update')
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        self.assertEqual(notification.data['application_id'], 123)
        
    def test_notification_str(self):
        """Test string representation of notification"""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='new_opportunity',
            title='New Opportunity Available',
            message='Check out this new internship'
        )
        
        expected_str = f"{self.user.username} - New Opportunity Available"
        self.assertEqual(str(notification), expected_str)
        
    def test_notification_ordering(self):
        """Test notifications are ordered by creation date (newest first)"""
        # Create notifications with slight time difference
        notification1 = Notification.objects.create(
            recipient=self.user,
            notification_type='system_announcement',
            title='First Notification',
            message='First message'
        )
        
        notification2 = Notification.objects.create(
            recipient=self.user,
            notification_type='system_announcement',
            title='Second Notification',
            message='Second message'
        )
        
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], notification2)  # Newest first
        self.assertEqual(notifications[1], notification1)
        
    def test_notification_types(self):
        """Test all notification types are valid"""
        valid_types = [
            'application_status',
            'new_opportunity',
            'deadline_reminder',
            'message_received',
            'interview_scheduled',
            'system_announcement'
        ]
        
        for notification_type in valid_types:
            notification = Notification.objects.create(
                recipient=self.user,
                notification_type=notification_type,
                title=f'Test {notification_type}',
                message='Test message'
            )
            self.assertEqual(notification.notification_type, notification_type)


class NotificationSettingsModelTest(TestCase):
    """Test NotificationSettings model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='settingsuser',
            email='settings@example.com',
            password='testpass123',
            user_type='student'
        )
        
    def test_notification_settings_creation(self):
        """Test creating notification settings"""
        settings = NotificationSettings.objects.create(
            user=self.user,
            email_notifications=True,
            push_notifications=False,
            application_updates=True
        )
        
        self.assertEqual(settings.user, self.user)
        self.assertTrue(settings.email_notifications)
        self.assertFalse(settings.push_notifications)
        self.assertTrue(settings.application_updates)
        
    def test_notification_settings_defaults(self):
        """Test default values for notification settings"""
        settings = NotificationSettings.objects.create(user=self.user)
        
        # Check all defaults are True
        self.assertTrue(settings.email_notifications)
        self.assertTrue(settings.push_notifications)
        self.assertTrue(settings.application_updates)
        self.assertTrue(settings.new_opportunities)
        self.assertTrue(settings.deadline_reminders)
        self.assertTrue(settings.messages)
        self.assertTrue(settings.system_announcements)
        
    def test_notification_settings_str(self):
        """Test string representation of notification settings"""
        settings = NotificationSettings.objects.create(user=self.user)
        expected_str = f"Notification settings for {self.user.username}"
        self.assertEqual(str(settings), expected_str)


class NotificationSerializerTest(TestCase):
    """Test notification serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='serializeruser',
            email='serializer@example.com',
            password='testpass123',
            user_type='student'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type='application_status',
            title='Test Notification',
            message='Test message',
            data={'test': 'data'}
        )
        
    def test_notification_serializer(self):
        """Test NotificationSerializer serialization"""
        serializer = NotificationSerializer(self.notification)
        data = serializer.data
        
        self.assertEqual(data['id'], self.notification.id)
        self.assertEqual(data['notification_type'], 'application_status')
        self.assertEqual(data['title'], 'Test Notification')
        self.assertEqual(data['message'], 'Test message')
        self.assertEqual(data['data'], {'test': 'data'})
        self.assertFalse(data['is_read'])
        self.assertIsNone(data['read_at'])
        
    def test_notification_settings_serializer(self):
        """Test NotificationSettingsSerializer"""
        settings = NotificationSettings.objects.create(
            user=self.user,
            email_notifications=False,
            push_notifications=True,
            application_updates=False
        )
        
        serializer = NotificationSettingsSerializer(settings)
        data = serializer.data
        
        self.assertFalse(data['email_notifications'])
        self.assertTrue(data['push_notifications'])
        self.assertFalse(data['application_updates'])
        self.assertTrue(data['new_opportunities'])  # Default value


class NotificationAPITest(APITestCase):
    """Test notification API endpoints"""
    
    def setUp(self):
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            user_type='student'
        )
        self.org_user = User.objects.create_user(
            username='orguser',
            email='org@example.com',
            password='testpass123',
            user_type='organization'
        )
        
        # Create test notifications
        self.notification1 = Notification.objects.create(
            recipient=self.student_user,
            notification_type='application_status',
            title='Application Approved',
            message='Congratulations! Your application has been approved.'
        )
        
        self.notification2 = Notification.objects.create(
            recipient=self.student_user,
            notification_type='new_opportunity',
            title='New Internship',
            message='A new internship opportunity is available.'
        )
        
        self.client = APIClient()
        
    def test_notification_list_authenticated(self):
        """Test listing notifications for authenticated user"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check notifications are ordered correctly (newest first)
        self.assertEqual(response.data['results'][0]['id'], self.notification2.id)
        self.assertEqual(response.data['results'][1]['id'], self.notification1.id)
        
    def test_notification_list_unauthenticated(self):
        """Test listing notifications without authentication"""
        url = reverse('notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_notification_list_user_isolation(self):
        """Test users only see their own notifications"""
        self.client.force_authenticate(user=self.org_user)
        url = reverse('notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
    def test_notification_detail(self):
        """Test retrieving a specific notification"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('notification-detail', args=[self.notification1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Application Approved')
        
    def test_notification_detail_wrong_user(self):
        """Test accessing notification of another user"""
        self.client.force_authenticate(user=self.org_user)
        url = reverse('notification-detail', args=[self.notification1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        self.assertFalse(self.notification1.is_read)
        self.assertIsNone(self.notification1.read_at)
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('mark-notification-read', args=[self.notification1.id])
        response = self.client.put(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertIsNotNone(self.notification1.read_at)
        
    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('mark-all-notifications-read')
        response = self.client.put(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Marked 2 notifications as read', response.data['message'])
        
        # Check all notifications are marked as read
        notifications = Notification.objects.filter(recipient=self.student_user)
        for notification in notifications:
            self.assertTrue(notification.is_read)
            self.assertIsNotNone(notification.read_at)
            
    def test_delete_notification(self):
        """Test deleting a notification"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('delete-notification', args=[self.notification1.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check notification is deleted
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=self.notification1.id)
            
    def test_notification_stats(self):
        """Test notification statistics endpoint"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('notification-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_notifications'], 2)
        self.assertEqual(response.data['unread_notifications'], 2)
        self.assertIn('notifications_by_type', response.data)


class NotificationSettingsAPITest(APITestCase):
    """Test notification settings API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='settingsuser',
            email='settings@example.com',
            password='testpass123',
            user_type='student'
        )
        self.client = APIClient()
        
    def test_get_notification_settings(self):
        """Test retrieving notification settings"""
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-settings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check default values
        self.assertTrue(response.data['email_notifications'])
        self.assertTrue(response.data['push_notifications'])
        self.assertTrue(response.data['application_updates'])
        
    def test_update_notification_settings(self):
        """Test updating notification settings"""
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-settings')
        
        data = {
            'email_notifications': False,
            'push_notifications': True,
            'application_updates': False,
            'new_opportunities': True,
            'deadline_reminders': False,
            'messages': True,
            'system_announcements': False
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['email_notifications'])
        self.assertTrue(response.data['push_notifications'])
        self.assertFalse(response.data['application_updates'])
        
        # Verify in database
        settings = NotificationSettings.objects.get(user=self.user)
        self.assertFalse(settings.email_notifications)
        self.assertTrue(settings.push_notifications)
        self.assertFalse(settings.application_updates)


class NotificationWorkflowTest(TestCase):
    """Test notification workflows for different user types"""
    
    def setUp(self):
        # Create student user and profile
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            user_type='student'
        )
        Profile.objects.create(user=self.student_user)
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        # Create organization user
        self.org_user = User.objects.create_user(
            username='orguser',
            email='org@example.com',
            password='testpass123',
            user_type='organization'
        )
        Profile.objects.create(user=self.org_user)
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            organization_type='company',
            description='Test organization',
            website='https://test.com',
            email='test@organization.com',
            country='Test Country',
            city='Test City'
        )
        
    def test_student_notification_creation(self):
        """Test creating notifications for students"""
        notification = Notification.objects.create(
            recipient=self.student_user,
            notification_type='new_opportunity',
            title='New Opportunity Available',
            message='A new internship is available that matches your profile'
        )
        
        self.assertEqual(notification.recipient, self.student_user)
        self.assertEqual(notification.notification_type, 'new_opportunity')
        
    def test_organization_notification_creation(self):
        """Test creating notifications for organizations"""
        notification = Notification.objects.create(
            recipient=self.org_user,
            notification_type='application_status',
            title='New Application Received',
            message='You have received a new application for your internship posting'
        )
        
        self.assertEqual(notification.recipient, self.org_user)
        self.assertEqual(notification.notification_type, 'application_status')
        
    def test_notification_with_future_events(self):
        """Test notifications for deadline reminders"""
        # Create deadline reminder notification
        future_date = timezone.now() + timedelta(days=7)
        notification = Notification.objects.create(
            recipient=self.student_user,
            notification_type='deadline_reminder',
            title='Application Deadline Approaching',
            message='The deadline for your application is tomorrow',
            data={'deadline': future_date.isoformat()}
        )
        
        self.assertEqual(notification.notification_type, 'deadline_reminder')
        self.assertIn('deadline', notification.data)


class NotificationIntegrationTest(APITestCase):
    """Test integration between notifications and other systems"""
    
    def setUp(self):
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            user_type='student'
        )
        
        self.org_user = User.objects.create_user(
            username='orguser',
            email='org@example.com',
            password='testpass123',
            user_type='organization'
        )
        
        self.client = APIClient()
        
    def test_notification_permissions(self):
        """Test notification permission isolation between users"""
        # Create notification for student
        student_notification = Notification.objects.create(
            recipient=self.student_user,
            notification_type='application_status',
            title='Student Notification',
            message='This is for the student'
        )
        
        # Create notification for organization
        org_notification = Notification.objects.create(
            recipient=self.org_user,
            notification_type='application_status',
            title='Organization Notification',
            message='This is for the organization'
        )
        
        # Test student can only see their notifications
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('notification-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Student Notification')
        
        # Test organization can only see their notifications
        self.client.force_authenticate(user=self.org_user)
        response = self.client.get(reverse('notification-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Organization Notification')
        
    def test_bulk_notification_operations(self):
        """Test bulk operations on notifications"""
        # Create multiple notifications
        notifications = []
        for i in range(5):
            notification = Notification.objects.create(
                recipient=self.student_user,
                notification_type='system_announcement',
                title=f'Notification {i}',
                message=f'Message {i}'
            )
            notifications.append(notification)
            
        self.client.force_authenticate(user=self.student_user)
        
        # Mark all as read
        response = self.client.put(reverse('mark-all-notifications-read'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all are read
        for notification in notifications:
            notification.refresh_from_db()
            self.assertTrue(notification.is_read)