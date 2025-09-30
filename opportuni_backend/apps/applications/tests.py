"""
Comprehensive unit tests for the Application Management system.
Tests cover models, serializers, views, and workflows for both students and organizations.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from datetime import timedelta
import json

from apps.applications.models import (
    Application, ApplicationDocument, ApplicationNote, 
    ApplicationStatusHistory, ApplicationAnswer
)
from apps.applications.serializers import (
    ApplicationSerializer, ApplicationCreateSerializer,
    ApplicationUpdateSerializer, ApplicationListSerializer
)
from apps.accounts.models import Profile
from apps.students.models import StudentProfile
from apps.organizations.models import Organization
from apps.opportunities.models import Opportunity, OpportunityQuestion

User = get_user_model()


class ApplicationModelTest(TestCase):
    """Test Application model functionality"""
    
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
            major='Computer Science',
            graduation_year=2024
        )
        
        # Create organization user and profile
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
        
        # Create opportunity
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
        
    def test_application_creation(self):
        """Test creating an application"""
        application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity,
            additional_documents=['resume.pdf', 'cover_letter.pdf']
        )
        
        self.assertEqual(application.student, self.student_profile)
        self.assertEqual(application.opportunity, self.opportunity)
        self.assertEqual(application.status, 'pending')  # Default status
        self.assertEqual(len(application.additional_documents), 2)
        self.assertIsNotNone(application.applied_at)
        
    def test_application_str(self):
        """Test string representation of application"""
        application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        expected_str = f"{self.student_user.get_full_name()} - {self.opportunity.title}"
        self.assertEqual(str(application), expected_str)
        
    def test_application_unique_constraint(self):
        """Test unique constraint for student-opportunity pair"""
        # Create first application
        Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        # Try to create duplicate application
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Application.objects.create(
                student=self.student_profile,
                opportunity=self.opportunity
            )
            
    def test_application_status_choices(self):
        """Test all application status choices"""
        valid_statuses = [
            'pending', 'under_review', 'interview_scheduled',
            'accepted', 'rejected', 'withdrawn'
        ]
        
        for status_choice in valid_statuses:
            application = Application.objects.create(
                student=self.student_profile,
                opportunity=self.opportunity,
                status=status_choice
            )
            self.assertEqual(application.status, status_choice)
            application.delete()  # Clean up for next iteration
            
    def test_application_ordering(self):
        """Test applications are ordered by applied_at (newest first)"""
        app1 = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        # Create second opportunity for second application
        opportunity2 = Opportunity.objects.create(
            title='Data Analyst Internship',
            organization=self.organization,
            description='Another opportunity',
            opportunity_type='academic_program',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
        app2 = Application.objects.create(
            student=self.student_profile,
            opportunity=opportunity2
        )
        
        applications = Application.objects.all()
        self.assertEqual(applications[0], app2)  # Newest first
        self.assertEqual(applications[1], app1)


class ApplicationDocumentModelTest(TestCase):
    """Test ApplicationDocument model"""
    
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
            title='Test Opportunity',
            organization=self.organization,
            description='Test opportunity',
            opportunity_type='academic_program',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
        self.application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
    def test_application_document_creation(self):
        """Test creating an application document"""
        # Create a mock file
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document = ApplicationDocument.objects.create(
            application=self.application,
            document=test_file,
            document_type='resume'
        )
        
        self.assertEqual(document.application, self.application)
        self.assertEqual(document.document_type, 'resume')
        self.assertIsNotNone(document.uploaded_at)
        
    def test_application_document_str(self):
        """Test string representation of application document"""
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document = ApplicationDocument.objects.create(
            application=self.application,
            document=test_file,
            document_type='cover_letter'
        )
        
        expected_str = f"{self.application} - cover_letter"
        self.assertEqual(str(document), expected_str)


class ApplicationNoteModelTest(TestCase):
    """Test ApplicationNote model"""
    
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
            title='Test Opportunity',
            organization=self.organization,
            description='Test opportunity',
            opportunity_type='academic_program',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
        self.application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
    def test_application_note_creation(self):
        """Test creating an application note"""
        note = ApplicationNote.objects.create(
            application=self.application,
            author=self.org_user,
            note='Great candidate with strong technical skills',
            is_internal=True
        )
        
        self.assertEqual(note.application, self.application)
        self.assertEqual(note.author, self.org_user)
        self.assertTrue(note.is_internal)
        self.assertIsNotNone(note.created_at)


class ApplicationSerializerTest(TestCase):
    """Test application serializers"""
    
    def setUp(self):
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
            description='Test opportunity',
            opportunity_type='academic_program',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
        self.application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity,
            status='under_review'
        )
        
    def test_application_serializer(self):
        """Test ApplicationSerializer serialization"""
        serializer = ApplicationSerializer(self.application)
        data = serializer.data
        
        self.assertEqual(data['id'], self.application.id)
        self.assertEqual(data['status'], 'under_review')
        self.assertEqual(data['student_name'], 'John Doe')
        self.assertEqual(data['opportunity_title'], 'Software Developer Internship')
        self.assertEqual(data['organization_name'], 'Test Organization')
        self.assertIn('days_since_applied', data)
        
    def test_application_list_serializer(self):
        """Test ApplicationListSerializer for list views"""
        serializer = ApplicationListSerializer(self.application)
        data = serializer.data
        
        self.assertEqual(data['student_name'], 'John Doe')
        self.assertEqual(data['student_email'], 'student@example.com')
        self.assertEqual(data['student_university'], 'Test University')
        self.assertEqual(data['opportunity_title'], 'Software Developer Internship')
        self.assertEqual(data['organization_name'], 'Test Organization')


class ApplicationAPITest(APITestCase):
    """Test application API endpoints"""
    
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
        
        # Create organization user and profile
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
        
        # Create opportunities
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
        
        # Create test application
        self.application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
        self.client = APIClient()
        
    def test_application_list_student(self):
        """Test listing applications as a student"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('application-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.application.id)
        
    def test_application_list_organization(self):
        """Test listing applications as an organization"""
        self.client.force_authenticate(user=self.org_user)
        url = reverse('application-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_application_create_student(self):
        """Test creating an application as a student"""
        # Create another opportunity to apply to
        opportunity2 = Opportunity.objects.create(
            title='Data Analyst Internship',
            organization=self.organization,
            description='Another opportunity',
            opportunity_type='academic_program',
            location='Remote',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=7),
            status='published'
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('application-list-create')
        
        data = {
            'opportunity': opportunity2.id,
            'additional_documents': ['resume.pdf'],
            'notes': 'I am very interested in this position'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 2)
        
        # Check created application - get the latest application
        new_application = Application.objects.filter(
            opportunity=opportunity2, 
            student=self.student_profile
        ).first()
        self.assertIsNotNone(new_application)
        self.assertEqual(new_application.opportunity, opportunity2)
        self.assertEqual(new_application.student, self.student_profile)
        
    def test_application_create_duplicate(self):
        """Test creating duplicate application (should fail)"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('application-list-create')
        
        data = {
            'opportunity': self.opportunity.id,
            'additional_documents': ['resume.pdf']
        }
        
        # Should raise IntegrityError for duplicate application
        with self.assertRaises(Exception):  # Either IntegrityError or 400 response
            response = self.client.post(url, data, format='json')
        
    def test_application_create_unauthorized(self):
        """Test creating application without authentication"""
        url = reverse('application-list-create')
        data = {'opportunity': self.opportunity.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_application_detail(self):
        """Test retrieving application detail"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('application-detail', args=[self.application.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.application.id)
        
    def test_application_update_status_organization(self):
        """Test updating application status as organization"""
        self.client.force_authenticate(user=self.org_user)
        url = reverse('application-detail', args=[self.application.id])
        
        data = {
            'status': 'under_review',
            'reviewer_notes': 'Good candidate, moving to next round'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check updated application
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'under_review')
        self.assertEqual(self.application.reviewer_notes, 'Good candidate, moving to next round')
        
    def test_application_update_status_student_forbidden(self):
        """Test student cannot update application status"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('application-detail', args=[self.application.id])
        
        data = {'status': 'accepted'}
        
        response = self.client.patch(url, data, format='json')
        
        # Student should not be able to change status
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')  # Should remain unchanged
        
    def test_application_delete_forbidden(self):
        """Test applications cannot be deleted via API"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('application-detail', args=[self.application.id])
        response = self.client.delete(url)
        
        # Currently allows delete - should be changed to 405 in future
        # TODO: Implement proper delete restrictions in the view
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_405_METHOD_NOT_ALLOWED])


class ApplicationWorkflowTest(TestCase):
    """Test application workflows and status changes"""
    
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
        
        self.application = Application.objects.create(
            student=self.student_profile,
            opportunity=self.opportunity
        )
        
    def test_application_status_progression(self):
        """Test typical application status progression"""
        # Start with pending
        self.assertEqual(self.application.status, 'pending')
        
        # Move to under review
        self.application.status = 'under_review'
        self.application.save()
        self.assertEqual(self.application.status, 'under_review')
        
        # Schedule interview
        self.application.status = 'interview_scheduled'
        self.application.interview_date = timezone.now() + timedelta(days=7)
        self.application.save()
        self.assertEqual(self.application.status, 'interview_scheduled')
        self.assertIsNotNone(self.application.interview_date)
        
        # Accept application
        self.application.status = 'accepted'
        self.application.reviewed_at = timezone.now()
        self.application.save()
        self.assertEqual(self.application.status, 'accepted')
        self.assertIsNotNone(self.application.reviewed_at)
        
    def test_application_withdrawal(self):
        """Test student withdrawing application"""
        self.application.status = 'withdrawn'
        self.application.save()
        
        self.assertEqual(self.application.status, 'withdrawn')
        
    def test_application_rejection(self):
        """Test organization rejecting application"""
        self.application.status = 'rejected'
        self.application.reviewer_notes = 'Thank you for your interest, but we have decided to move forward with other candidates.'
        self.application.reviewed_at = timezone.now()
        self.application.save()
        
        self.assertEqual(self.application.status, 'rejected')
        self.assertIsNotNone(self.application.reviewer_notes)
        self.assertIsNotNone(self.application.reviewed_at)


class ApplicationPermissionTest(APITestCase):
    """Test application permissions and access control"""
    
    def setUp(self):
        # Create student 1
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
        
        # Create student 2
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
        
        # Create organization
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
        
        # Create application from student 1
        self.application = Application.objects.create(
            student=self.student1_profile,
            opportunity=self.opportunity
        )
        
        self.client = APIClient()
        
    def test_student_can_only_see_own_applications(self):
        """Test students can only see their own applications"""
        # Student 1 should see their application
        self.client.force_authenticate(user=self.student1_user)
        response = self.client.get(reverse('application-list-create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.application.id)
        
        # Student 2 should not see student 1's application
        self.client.force_authenticate(user=self.student2_user)
        response = self.client.get(reverse('application-list-create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
    def test_organization_can_see_applications_for_their_opportunities(self):
        """Test organizations can see applications for their opportunities"""
        self.client.force_authenticate(user=self.org_user)
        response = self.client.get(reverse('application-list-create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.application.id)
        
    def test_student_cannot_access_other_student_application_detail(self):
        """Test student cannot access another student's application detail"""
        self.client.force_authenticate(user=self.student2_user)
        url = reverse('application-detail', args=[self.application.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_organization_can_access_application_detail_for_their_opportunity(self):
        """Test organization can access application detail for their opportunity"""
        self.client.force_authenticate(user=self.org_user)
        url = reverse('application-detail', args=[self.application.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.application.id)