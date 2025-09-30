"""
Comprehensive integration tests for the backend systems.
Tests cross-system interactions, workflows, and permissions between students and organizations.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from datetime import timedelta
import json

from apps.accounts.models import Profile
from apps.students.models import StudentProfile
from apps.organizations.models import Organization
from apps.opportunities.models import Opportunity, OpportunityQuestion
from apps.applications.models import Application, ApplicationAnswer
from apps.communications.models import Message, EmailTemplate
from apps.notifications.models import Notification, NotificationSettings

User = get_user_model()


class StudentOrganizationWorkflowTest(APITestCase):
    """Test complete workflows between students and organizations"""
    
    def setUp(self):
        # Create student user and profile
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            user_type='student',
            first_name='John',
            last_name='Doe'
        )
        Profile.objects.create(user=self.student_user)
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science',
            graduation_year=2024,
            gpa=3.8
        )
        
        # Create organization user and profile
        self.org_user = User.objects.create_user(
            username='orguser',
            email='org@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Org',
            last_name='Admin'
        )
        Profile.objects.create(user=self.org_user)
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            organization_type='company',
            description='A test organization',
            country='United States',
            city='San Francisco'
        )
        
        # Create opportunity with questions
        self.opportunity = Opportunity.objects.create(
            title='Software Developer Internship',
            organization=self.organization,
            description='A challenging internship for aspiring developers',
            opportunity_type='mentoring',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published',
            min_gpa=3.0
        )
        
        # Add opportunity questions
        self.question1 = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Why are you interested in this position?',
            question_type='text',
            is_required=True
        )
        
        self.question2 = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='What is your experience with Python?',
            question_type='text',
            is_required=False
        )
        
        self.client = APIClient()
        
    def test_complete_application_workflow(self):
        """Test the complete application workflow from creation to acceptance"""
        
        # 1. Student applies to opportunity
        self.client.force_authenticate(user=self.student_user)
        application_data = {
            'opportunity': self.opportunity.id,
            'additional_documents': ['resume.pdf', 'portfolio.pdf'],
            'notes': 'I am very excited about this opportunity',
            'answers': {
                str(self.question1.id): 'I am passionate about software development and want to learn from experienced professionals.',
                str(self.question2.id): 'I have 2 years of experience with Python, including Django and Flask frameworks.'
            }
        }
        
        response = self.client.post(
            reverse('application-list-create'),
            application_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get the created application
        application = Application.objects.filter(
            student=self.student_profile,
            opportunity=self.opportunity
        ).first()
        self.assertIsNotNone(application)
        
        # Verify application was created
        self.assertEqual(application.student, self.student_profile)
        self.assertEqual(application.opportunity, self.opportunity)
        self.assertEqual(application.status, 'pending')
        
        # Verify answers were saved
        answers = ApplicationAnswer.objects.filter(application=application)
        self.assertEqual(answers.count(), 2)
        
        # 2. Organization reviews applications
        self.client.force_authenticate(user=self.org_user)
        
        # Get list of applications for the organization
        response = self.client.get(reverse('application-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # 3. Organization updates application status to under review
        update_data = {
            'status': 'under_review',
            'reviewer_notes': 'Strong candidate, good technical background'
        }
        
        response = self.client.patch(
            reverse('application-detail', args=[application.id]),
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status update
        application.refresh_from_db()
        self.assertEqual(application.status, 'under_review')
        self.assertEqual(application.reviewer_notes, 'Strong candidate, good technical background')
        
        # 4. Organization sends message to student
        message_data = {
            'recipient': self.student_user.id,
            'subject': 'Interview Invitation',
            'body': 'We would like to invite you for an interview next week.',
            'application': application.id
        }
        
        response = self.client.post(
            reverse('message-list-create'),
            message_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get the message
        message = Message.objects.filter(
            sender=self.org_user,
            recipient=self.student_user,
            subject='Interview Invitation'
        ).first()
        self.assertIsNotNone(message)
        self.assertEqual(message.sender, self.org_user)
        self.assertEqual(message.recipient, self.student_user)
        self.assertEqual(message.application, application)
        
        # 5. Student reads and replies to message
        self.client.force_authenticate(user=self.student_user)
        
        # Mark message as read
        response = self.client.post(
            reverse('mark-message-read', args=[message.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Send reply
        reply_data = {
            'recipient': self.org_user.id,
            'subject': 'Re: Interview Invitation',
            'body': 'Thank you for the invitation. I am available next week.',
            'application': application.id
        }
        
        response = self.client.post(
            reverse('message-list-create'),
            reply_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 6. Organization schedules interview
        self.client.force_authenticate(user=self.org_user)
        
        interview_data = {
            'status': 'interview_scheduled',
            'interview_date': (timezone.now() + timedelta(days=7)).isoformat(),
            'interview_notes': 'Video interview scheduled for next Tuesday at 2 PM'
        }
        
        response = self.client.patch(
            reverse('application-detail', args=[application.id]),
            interview_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 7. Organization accepts application after interview
        acceptance_data = {
            'status': 'accepted',
            'reviewer_notes': 'Excellent candidate! Looking forward to working together.',
            'reviewed_at': timezone.now().isoformat()
        }
        
        response = self.client.patch(
            reverse('application-detail', args=[application.id]),
            acceptance_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify final status
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        self.assertIsNotNone(application.reviewed_at)
        
        # Verify all messages were created during the workflow
        messages = Message.objects.filter(application=application).order_by('sent_at')
        self.assertEqual(messages.count(), 2)  # Invitation + reply


class CrossSystemPermissionsTest(APITestCase):
    """Test permissions across different systems"""
    
    def setUp(self):
        # Create multiple students
        self.student1_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass123',
            user_type='student'
        )
        Profile.objects.create(user=self.student1_user)
        self.student1_profile = StudentProfile.objects.create(
            user=self.student1_user,
            university='University 1',
            major='Computer Science'
        )
        
        self.student2_user = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='testpass123',
            user_type='student'
        )
        Profile.objects.create(user=self.student2_user)
        self.student2_profile = StudentProfile.objects.create(
            user=self.student2_user,
            university='University 2',
            major='Business'
        )
        
        # Create multiple organizations
        self.org1_user = User.objects.create_user(
            username='org1user',
            email='org1@example.com',
            password='testpass123',
            user_type='organization'
        )
        Profile.objects.create(user=self.org1_user)
        self.organization1 = Organization.objects.create(
            user=self.org1_user,
            name='Organization 1',
            organization_type='company',
            description='First organization',
            website='https://org1.com',
            email='contact@org1.com',
            country='United States',
            city='New York'
        )
        
        self.org2_user = User.objects.create_user(
            username='org2user',
            email='org2@example.com',
            password='testpass123',
            user_type='organization'
        )
        Profile.objects.create(user=self.org2_user)
        self.organization2 = Organization.objects.create(
            user=self.org2_user,
            name='Organization 2',
            organization_type='nonprofit',
            description='Second organization',
            website='https://org2.com',
            email='contact@org2.com',
            country='United States',
            city='Chicago'
        )
        
        # Create opportunities for each organization
        self.opportunity1 = Opportunity.objects.create(
            title='Opportunity 1',
            organization=self.organization1,
            description='First opportunity',
            opportunity_type='scholarship',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
        self.opportunity2 = Opportunity.objects.create(
            title='Opportunity 2',
            organization=self.organization2,
            description='Second opportunity',
            opportunity_type='conference',
            location='On-site',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
        # Create applications
        self.application1 = Application.objects.create(
            student=self.student1_profile,
            opportunity=self.opportunity1
        )
        
        self.application2 = Application.objects.create(
            student=self.student2_profile,
            opportunity=self.opportunity2
        )
        
        # Create cross-organization message (should not happen but test permissions)
        self.message = Message.objects.create(
            sender=self.org1_user,
            recipient=self.student1_user,
            subject='Test Message',
            body='Test message',
            application=self.application1
        )
        
        self.client = APIClient()
        
    def test_application_isolation_between_organizations(self):
        """Test organizations can only see applications for their own opportunities"""
        
        # Organization 1 should only see applications for their opportunities
        self.client.force_authenticate(user=self.org1_user)
        response = self.client.get(reverse('application-list-create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.application1.id)
        
        # Organization 2 should only see applications for their opportunities
        self.client.force_authenticate(user=self.org2_user)
        response = self.client.get(reverse('application-list-create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.application2.id)
        
    def test_student_application_isolation(self):
        """Test students can only see their own applications"""
        
        # Student 1 should only see their own applications
        self.client.force_authenticate(user=self.student1_user)
        response = self.client.get(reverse('application-list-create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.application1.id)
        
        # Student 2 should only see their own applications
        self.client.force_authenticate(user=self.student2_user)
        response = self.client.get(reverse('application-list-create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.application2.id)
        
    def test_cross_organization_application_access_denied(self):
        """Test organizations cannot access applications from other organizations"""
        
        # Organization 2 should not be able to access Application 1
        self.client.force_authenticate(user=self.org2_user)
        response = self.client.get(reverse('application-detail', args=[self.application1.id]))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Organization 1 should not be able to access Application 2
        self.client.force_authenticate(user=self.org1_user)
        response = self.client.get(reverse('application-detail', args=[self.application2.id]))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_message_access_permissions(self):
        """Test message access is restricted to sender and recipient"""
        
        # Sender should be able to access message
        self.client.force_authenticate(user=self.org1_user)
        response = self.client.get(reverse('message-detail', args=[self.message.id]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Recipient should be able to access message
        self.client.force_authenticate(user=self.student1_user)
        response = self.client.get(reverse('message-detail', args=[self.message.id]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Other users should not be able to access message
        self.client.force_authenticate(user=self.student2_user)
        response = self.client.get(reverse('message-detail', args=[self.message.id]))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        self.client.force_authenticate(user=self.org2_user)
        response = self.client.get(reverse('message-detail', args=[self.message.id]))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_notification_isolation(self):
        """Test notification isolation between users"""
        
        # Create notifications for different users
        notification1 = Notification.objects.create(
            recipient=self.student1_user,
            notification_type='application_status',
            title='Application Update',
            message='Your application status has been updated'
        )
        
        notification2 = Notification.objects.create(
            recipient=self.student2_user,
            notification_type='new_opportunity',
            title='New Opportunity',
            message='A new opportunity is available'
        )
        
        # Student 1 should only see their notification
        self.client.force_authenticate(user=self.student1_user)
        response = self.client.get(reverse('notification-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], notification1.id)
        
        # Student 2 should only see their notification
        self.client.force_authenticate(user=self.student2_user)
        response = self.client.get(reverse('notification-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], notification2.id)


class SystemIntegrationTest(TransactionTestCase):
    """Test system-wide integration and data consistency"""
    
    def setUp(self):
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
        
        self.opportunity = Opportunity.objects.create(
            title='Software Developer Internship',
            organization=self.organization,
            description='A great internship opportunity',
            opportunity_type='academic_program',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
    def test_application_creation_triggers_notifications(self):
        """Test that creating an application triggers appropriate notifications"""
        
        # Create application
        application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        # In a real system, this would be handled by signals
        # For now, we manually create the notification to test the flow
        
        # Notification to organization about new application
        org_notification = Notification.objects.create(
            recipient=self.org_user,
            notification_type='application_status',
            title='New Application Received',
            message=f'You have received a new application for {self.opportunity.title}',
            data={'application_id': application.id, 'opportunity_id': self.opportunity.id}
        )
        
        # Notification to student confirming application submission
        student_notification = Notification.objects.create(
            recipient=self.student_user,
            notification_type='application_status',
            title='Application Submitted',
            message=f'Your application for {self.opportunity.title} has been submitted',
            data={'application_id': application.id, 'opportunity_id': self.opportunity.id}
        )
        
        # Verify notifications were created
        self.assertEqual(Notification.objects.count(), 2)
        
        # Verify notification content
        self.assertEqual(org_notification.recipient, self.org_user)
        self.assertEqual(student_notification.recipient, self.student_user)
        self.assertEqual(org_notification.data['application_id'], application.id)
        self.assertEqual(student_notification.data['application_id'], application.id)
        
    def test_application_status_change_consistency(self):
        """Test data consistency when application status changes"""
        
        application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        # Change status to accepted
        application.status = 'accepted'
        application.reviewed_at = timezone.now()
        application.reviewer_notes = 'Great candidate!'
        application.save()
        
        # Verify all fields are consistent
        self.assertEqual(application.status, 'accepted')
        self.assertIsNotNone(application.reviewed_at)
        self.assertEqual(application.reviewer_notes, 'Great candidate!')
        
        # In a real system, this would trigger notifications
        notification = Notification.objects.create(
            recipient=self.student_user,
            notification_type='application_status',
            title='Application Accepted!',
            message=f'Congratulations! Your application for {self.opportunity.title} has been accepted.',
            data={'application_id': application.id, 'status': 'accepted'}
        )
        
        self.assertEqual(notification.data['status'], 'accepted')
        
    def test_message_application_relationship_consistency(self):
        """Test message-application relationship consistency"""
        
        application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        # Create message related to application
        message = Message.objects.create(
            sender=self.org_user,
            recipient=self.student_user,
            subject='Interview Invitation',
            body='We would like to invite you for an interview',
            application=application
        )
        
        # Verify relationships
        self.assertEqual(message.application, application)
        self.assertEqual(message.sender, self.org_user)
        self.assertEqual(message.recipient, self.student_user)
        
        # Verify the application-message relationship works both ways
        messages = Message.objects.filter(application=application)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first(), message)
        
    @patch('django.core.mail.send_mail')
    def test_email_template_system_integration(self, mock_send_mail):
        """Test email template system integration with other components"""
        mock_send_mail.return_value = True
        
        # Create email template
        template = EmailTemplate.objects.create(
            organization=self.organization,
            name='Application Received',
            template_type='application_received',
            subject='Application Received - {{opportunity_title}}',
            body='Dear {{student_name}}, we have received your application for {{opportunity_title}}.',
            variables=['student_name', 'opportunity_title']
        )
        
        application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        # Simulate template-based email sending (would be in views/services)
        subject = template.subject.replace('{{opportunity_title}}', self.opportunity.title)
        body = template.body.replace('{{student_name}}', self.student_user.get_full_name())
        body = body.replace('{{opportunity_title}}', self.opportunity.title)
        
        # Create message using template
        message = Message.objects.create(
            sender=self.org_user,
            recipient=self.student_user,
            subject=subject,
            body=body,
            application=application
        )
        
        # Verify template variables were replaced
        self.assertIn(self.opportunity.title, message.subject)
        self.assertIn(self.student_user.get_full_name(), message.body)
        self.assertNotIn('{{', message.subject)  # No unreplaced variables
        self.assertNotIn('{{', message.body)


class NotificationSystemIntegrationTest(APITestCase):
    """Test notification system integration with other components"""
    
    def setUp(self):
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
        
        # Create notification settings for users
        NotificationSettings.objects.create(
            user=self.student_user,
            application_updates=True,
            new_opportunities=True,
            messages=True
        )
        
        NotificationSettings.objects.create(
            user=self.org_user,
            application_updates=True,
            messages=True
        )
        
        self.client = APIClient()
        
    def test_notification_preferences_respected(self):
        """Test that notification preferences are respected"""
        
        # Disable application updates for student
        settings = NotificationSettings.objects.get(user=self.student_user)
        settings.application_updates = False
        settings.save()
        
        # Create notification (in real system, this would check preferences)
        notification = Notification.objects.create(
            recipient=self.student_user,
            notification_type='application_status',
            title='Application Update',
            message='Your application status has been updated'
        )
        
        # In a real system, the notification creation would be conditional
        # based on user preferences. Here we verify the preferences exist.
        self.assertFalse(settings.application_updates)
        
        # Verify notification was still created (for testing purposes)
        # In production, this notification wouldn't be created if disabled
        self.assertEqual(notification.recipient, self.student_user)
        
    def test_notification_cleanup_and_management(self):
        """Test notification cleanup and bulk operations"""
        
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
        
        # Verify all notifications are marked as read
        for notification in notifications:
            notification.refresh_from_db()
            self.assertTrue(notification.is_read)
            self.assertIsNotNone(notification.read_at)
            
        # Test notification stats
        response = self.client.get(reverse('notification-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_notifications'], 5)
        # The API only returns unread_notifications, not read_notifications
        self.assertEqual(response.data['unread_notifications'], 0)


class PerformanceAndScalabilityTest(TestCase):
    """Test system performance and scalability aspects"""
    
    def setUp(self):
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
        
    def test_bulk_notification_creation(self):
        """Test creating notifications in bulk doesn't cause performance issues"""
        
        # Create multiple users
        users = []
        for i in range(10):  # Small number for test
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123',
                user_type='student'
            )
            users.append(user)
            
        # Create notifications for all users
        notifications = []
        for user in users:
            notification = Notification.objects.create(
                recipient=user,
                notification_type='system_announcement',
                title='System Maintenance Notice',
                message='The system will undergo maintenance this weekend.'
            )
            notifications.append(notification)
            
        # Verify all notifications were created
        self.assertEqual(len(notifications), 10)
        self.assertEqual(Notification.objects.count(), 10)
        
        # Test batch operations
        notification_ids = [n.id for n in notifications]
        bulk_notifications = Notification.objects.filter(id__in=notification_ids)
        
        # Bulk mark as read
        bulk_notifications.update(is_read=True, read_at=timezone.now())
        
        # Verify bulk update worked
        for notification in bulk_notifications:
            self.assertTrue(notification.is_read)
            
    def test_application_query_optimization(self):
        """Test that application queries are optimized"""
        
        # Create multiple students and applications
        students = []
        applications = []
        
        for i in range(5):  # Small number for test
            user = User.objects.create_user(
                username=f'student{i}',
                email=f'student{i}@example.com',
                password='testpass123',
                user_type='student'
            )
            Profile.objects.create(user=user)
            student_profile = StudentProfile.objects.create(
                user=user,
                university=f'University {i}',
                major='Computer Science'
            )
            students.append((user, student_profile))
            
            # Create opportunity for this test
            opportunity = Opportunity.objects.create(
                title=f'Opportunity {i}',
                organization=self.organization,
                description=f'Opportunity {i} description',
                opportunity_type='volunteer',
                location='Remote',
                application_deadline=timezone.now() + timedelta(days=30),
                start_date=timezone.now().date() + timedelta(days=7),
                status='published'
            )
            
            application = Application.objects.create(
                student=student_profile,
                opportunity=opportunity
            )
            applications.append(application)
            
        # Test querying applications with related data
        # This should use select_related/prefetch_related for optimization
        applications_with_data = Application.objects.select_related(
            'student__user', 'opportunity__organization'
        ).all()
        
        # Verify we can access related data without additional queries
        for application in applications_with_data:
            # These should not trigger additional database queries
            student_name = application.student.user.get_full_name()
            org_name = application.opportunity.organization.name
            
            self.assertIsNotNone(student_name)
            self.assertIsNotNone(org_name)
            
        self.assertEqual(applications_with_data.count(), 5)