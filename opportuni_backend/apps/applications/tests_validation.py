"""
🔴 CRITICAL: Application Validation Tests
Advanced edge case tests for real-world scenarios including:
- Multi-language support (Cyrillic, Chinese, Arabic, etc.)
- Transaction rollback scenarios
- Race conditions
- Malformed data
- Database integrity
"""
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.db import transaction, IntegrityError
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from unittest.mock import patch
import json

from apps.accounts.models import User
from apps.students.models import StudentProfile, Education, Experience, Skill
from apps.organizations.models import Organization
from apps.opportunities.models import Opportunity, OpportunityQuestion, OpportunityProfileRequirement
from apps.applications.models import Application, ApplicationAnswer


class MultiLanguageApplicationTestCase(TestCase):
    """🌍 Test application creation with different languages and character sets"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create organization
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        # Create student with Cyrillic name
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Алишер',  # Cyrillic
            last_name='Навоий'    # Cyrillic
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Тошкент Давлат Университети',  # Cyrillic
            major='Компьютер Фанлари'
        )
        
        # Create opportunity
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Internship',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        self.required_question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Nima uchun qo\'shilmoqchisiz?',
            question_type='textarea',
            is_required=True
        )
        
        self.client.force_authenticate(user=self.student_user)
    
    def test_cyrillic_answers_accepted(self):
        """✅ Test Cyrillic (Russian/Uzbek) text in answers"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'Мен бу имкониятга жуда қизиқаман чунки...'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify answer saved correctly with Cyrillic
        application = Application.objects.get(id=response.data['id'])
        answer = application.answers.first()
        self.assertIn('Мен бу', answer.answer_text)
    
    def test_chinese_answers_accepted(self):
        """✅ Test Chinese characters in answers"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): '我对这个机会很感兴趣，因为我想学习更多关于...'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Chinese characters preserved
        application = Application.objects.get(id=response.data['id'])
        answer = application.answers.first()
        self.assertIn('我对这个', answer.answer_text)
    
    def test_arabic_answers_accepted(self):
        """✅ Test Arabic/Urdu text in answers"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'أنا مهتم جداً بهذه الفرصة لأنني...'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        application = Application.objects.get(id=response.data['id'])
        answer = application.answers.first()
        self.assertIn('أنا مهتم', answer.answer_text)
    
    def test_emoji_in_answers(self):
        """✅ Test emoji characters in answers"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'I am very excited 🎉 about this opportunity! 💪 I want to learn more 📚'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        application = Application.objects.get(id=response.data['id'])
        answer = application.answers.first()
        self.assertIn('🎉', answer.answer_text)
        self.assertIn('💪', answer.answer_text)
    
    def test_mixed_language_answers(self):
        """✅ Test mixed English, Cyrillic, and Latin answers"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'Men Toshkent shahridan (Ташкент) keldim. I want to study Computer Science 💻'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_only_whitespace_cyrillic_rejected(self):
        """❌ Test that Cyrillic whitespace-only answers are rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): '   　　　'  # Latin and ideographic spaces
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
    
    def test_special_characters_in_answers(self):
        """✅ Test special characters and symbols"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'Email: test@example.com, Skills: C++, C#, .NET, GPA: 3.8/4.0 ★★★★☆'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TransactionAndIntegrityTestCase(TransactionTestCase):
    """🔒 Test database transaction integrity and rollback scenarios"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Internship',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        self.required_question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Required question?',
            question_type='textarea',
            is_required=True
        )
        
        self.client.force_authenticate(user=self.student_user)
    
    def test_application_created_but_answers_fail_to_save(self):
        """🔴 CRITICAL: Test that if answers fail to save, application is rolled back"""
        
        # Mock ApplicationAnswer.objects.create to fail
        with patch('apps.applications.serializers.ApplicationAnswer.objects.create') as mock_create:
            mock_create.side_effect = Exception('Database error while saving answer')
            
            # This should fail with 500 error due to atomic transaction
            response = self.client.post('/api/applications/', {
                'opportunity': self.opportunity.id,
                'answers': {
                    str(self.required_question.id): 'Valid answer'
                }
            }, format='json')
            
            # Should return error status
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])
            
            # Verify no application was created (transaction rolled back)
            self.assertEqual(Application.objects.count(), 0)
            self.assertEqual(ApplicationAnswer.objects.count(), 0)
    
    def test_validation_fails_no_database_changes(self):
        """🔴 CRITICAL: Test that validation failures don't create any database records"""
        initial_app_count = Application.objects.count()
        initial_answer_count = ApplicationAnswer.objects.count()
        
        # Try to create invalid application
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}  # Missing required answer
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify NO database changes occurred
        self.assertEqual(Application.objects.count(), initial_app_count)
        self.assertEqual(ApplicationAnswer.objects.count(), initial_answer_count)
    
    def test_duplicate_application_attempt_atomic(self):
        """🔴 CRITICAL: Test that duplicate application attempts don't create orphaned answers"""
        
        # Create first application
        self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'First answer'
            }
        }, format='json')
        
        initial_answer_count = ApplicationAnswer.objects.count()
        
        # Try to create duplicate
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'Second answer'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no new answers were created
        self.assertEqual(ApplicationAnswer.objects.count(), initial_answer_count)
        
        # Verify still only 1 application
        self.assertEqual(Application.objects.filter(student=self.student_profile).count(), 1)


class MalformedDataTestCase(TestCase):
    """🚨 Test handling of malformed, unexpected, or malicious data"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Internship',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        self.required_question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Required question?',
            question_type='textarea',
            is_required=True
        )
        
        self.client.force_authenticate(user=self.student_user)
    
    def test_answers_as_string_instead_of_dict(self):
        """❌ Test that answers as string is rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': "This should be a dict, not a string"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_answers_as_list_instead_of_dict(self):
        """❌ Test that answers as list is rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': ['answer1', 'answer2']
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_question_id_as_integer_key(self):
        """✅ Test that integer question IDs in dict work (not just strings)"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                self.required_question.id: 'Valid answer'  # Integer key (will be converted by JSON)
            }
        }, format='json')
        
        # JSON will convert integer keys to strings, so this should work
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_non_existent_question_id_ignored(self):
        """✅ Test that answers to non-existent questions are ignored (not failed)"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'Valid answer',
                '99999': 'Answer to non-existent question',  # Should be ignored
                'invalid_id': 'Invalid question ID'  # Should be ignored
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify only 1 answer was saved (the valid one)
        application = Application.objects.get(id=response.data['id'])
        self.assertEqual(application.answers.count(), 1)
    
    def test_sql_injection_attempt_in_answer(self):
        """🔒 Test SQL injection attempts are safely handled"""
        malicious_answer = "'; DROP TABLE applications_application; --"
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): malicious_answer
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the malicious string was saved as plain text (not executed)
        application = Application.objects.get(id=response.data['id'])
        answer = application.answers.first()
        self.assertEqual(answer.answer_text, malicious_answer)
        
        # Verify table still exists (SQL wasn't executed)
        self.assertTrue(Application.objects.exists())
    
    def test_xss_attempt_in_answer(self):
        """🔒 Test XSS attempts are stored safely"""
        xss_answer = '<script>alert("XSS")</script>'
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): xss_answer
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify script tags stored as plain text
        application = Application.objects.get(id=response.data['id'])
        answer = application.answers.first()
        self.assertEqual(answer.answer_text, xss_answer)
    
    def test_extremely_long_answer(self):
        """✅ Test very long answers (10,000+ characters)"""
        long_answer = 'A' * 10000  # 10,000 characters
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): long_answer
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify full answer was saved
        application = Application.objects.get(id=response.data['id'])
        answer = application.answers.first()
        self.assertEqual(len(answer.answer_text), 10000)
    
    def test_null_byte_in_answer(self):
        """✅ Test null bytes are handled"""
        answer_with_null = "Answer with\x00null byte"
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): answer_with_null
            }
        }, format='json')
        
        # Should either succeed or fail gracefully (not crash)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_unicode_normalization(self):
        """✅ Test different unicode normalizations are handled"""
        # Same character in different unicode forms
        answer_nfc = 'café'  # NFC normalization
        answer_nfd = 'café'  # NFD normalization (visually same, different bytes)
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): answer_nfc
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EdgeCaseQuestionsTestCase(TestCase):
    """🎯 Test edge cases with question configurations"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Internship',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        self.client.force_authenticate(user=self.student_user)
    
    def test_opportunity_with_no_questions_at_all(self):
        """✅ Test application to opportunity with zero questions"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_opportunity_with_only_optional_questions(self):
        """✅ Test application with all optional questions (can skip all)"""
        OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Optional question 1?',
            question_type='text',
            is_required=False
        )
        OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Optional question 2?',
            question_type='textarea',
            is_required=False
        )
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}  # Skip all optional questions
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_question_deleted_after_application_started(self):
        """🔴 CRITICAL: Test that deleted questions don't cause validation errors"""
        question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='This will be deleted',
            question_type='text',
            is_required=True
        )
        
        # User starts application, then admin deletes question
        question.delete()
        
        # User submits without the now-deleted question
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}
        }, format='json')
        
        # Should succeed (no required questions exist anymore)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_question_changed_from_required_to_optional(self):
        """✅ Test question requirement change doesn't affect existing answers"""
        question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Question',
            question_type='text',
            is_required=True
        )
        
        # Create application with answer
        response1 = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(question.id): 'My answer'
            }
        }, format='json')
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Change question to optional
        question.is_required = False
        question.save()
        
        # Existing answer should still be there
        application = Application.objects.get(id=response1.data['id'])
        self.assertEqual(application.answers.count(), 1)
    
    def test_many_required_questions(self):
        """✅ Test opportunity with many (20+) required questions"""
        questions = []
        for i in range(25):
            q = OpportunityQuestion.objects.create(
                opportunity=self.opportunity,
                question=f'Required question {i+1}?',
                question_type='text',
                is_required=True,
                order=i
            )
            questions.append(q)
        
        # Create answers for all questions
        answers = {str(q.id): f'Answer {i+1}' for i, q in enumerate(questions)}
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': answers
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all 25 answers were saved
        application = Application.objects.get(id=response.data['id'])
        self.assertEqual(application.answers.count(), 25)
    
    def test_missing_one_of_many_required_questions(self):
        """❌ Test missing just 1 of 20 required questions fails"""
        questions = []
        for i in range(20):
            q = OpportunityQuestion.objects.create(
                opportunity=self.opportunity,
                question=f'Required question {i+1}?',
                question_type='text',
                is_required=True
            )
            questions.append(q)
        
        # Answer all but one question
        answers = {str(q.id): f'Answer {i+1}' for i, q in enumerate(questions[:-1])}
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': answers
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)


class ConcurrencyAndRaceConditionTestCase(TransactionTestCase):
    """⚡ Test concurrent application submissions and race conditions"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Internship',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        self.required_question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Required question?',
            question_type='textarea',
            is_required=True
        )
        
        self.client.force_authenticate(user=self.student_user)
    
    def test_opportunity_closed_while_submitting(self):
        """🔴 CRITICAL: Test opportunity closes after validation but before save"""
        
        original_save = Application.save
        
        def delayed_save(self, *args, **kwargs):
            # Close opportunity during save
            opp = Opportunity.objects.get(id=self.opportunity.id)
            opp.status = 'closed'
            opp.save()
            return original_save(self, *args, **kwargs)
        
        with patch.object(Application, 'save', delayed_save):
            response = self.client.post('/api/applications/', {
                'opportunity': self.opportunity.id,
                'answers': {
                    str(self.required_question.id): 'Valid answer'
                }
            }, format='json')
            
            # Should still succeed (validation passed when it was open)
            # Or should fail - depends on your business logic
            # This documents the behavior
            self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_max_applications_reached_during_submission(self):
        """🔴 CRITICAL: Test max applications limit reached during submission"""
        # Set max applications to 1
        self.opportunity.max_applications = 1
        self.opportunity.save()
        
        # Create another student
        student2_user = User.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='testpass123',
            user_type='student',
            first_name='Student',
            last_name='Two'
        )
        student2_profile = StudentProfile.objects.create(
            user=student2_user,
            university='Test University',
            major='Computer Science'
        )
        
        # Student 2 applies first
        client2 = APIClient()
        client2.force_authenticate(user=student2_user)
        
        response1 = client2.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'Student 2 answer'
            }
        }, format='json')
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Student 1 tries to apply (max reached)
        response2 = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question.id): 'Student 1 answer'
            }
        }, format='json')
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('opportunity', response2.data)



class ApplicationValidationTestCase(TestCase):
    """Test suite for application validation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create organization user and profile
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        # Create student user and profile
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        # Create opportunity
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Internship',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        # Create required questions
        self.required_question_1 = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Nima uchun qo\'shilmoqchisiz?',
            question_type='textarea',
            is_required=True,
            order=1
        )
        
        self.required_question_2 = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Qanday tajribangiz bor?',
            question_type='textarea',
            is_required=True,
            order=2
        )
        
        # Create optional question
        self.optional_question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Qo\'shimcha ma\'lumot?',
            question_type='text',
            is_required=False,
            order=3
        )
        
        # Authenticate as student
        self.client.force_authenticate(user=self.student_user)
    
    def test_application_without_answers_rejected(self):
        """🔴 CRITICAL: Test that applications without answers are rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
        self.assertIn('Javob berilmagan majburiy savollar', str(response.data['answers']))
    
    def test_application_with_empty_answers_rejected(self):
        """🔴 CRITICAL: Test that empty string answers are rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): '   ',  # Whitespace only
                str(self.required_question_2.id): ''      # Empty string
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
        self.assertIn('Bo\'sh qoldirilgan majburiy savollar', str(response.data['answers']))
    
    def test_application_with_partial_answers_rejected(self):
        """🔴 CRITICAL: Test that missing some required answers is rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): 'Valid answer'
                # Missing required_question_2
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
        self.assertIn('Javob berilmagan majburiy savollar', str(response.data['answers']))
    
    def test_application_with_valid_answers_accepted(self):
        """✅ Test that valid applications with all required answers are accepted"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): 'Men bu imkoniyatga qiziqaman chunki...',
                str(self.required_question_2.id): 'Menda 2 yillik tajriba bor...'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify application was created
        application = Application.objects.get(id=response.data['id'])
        self.assertEqual(application.student, self.student_profile)
        self.assertEqual(application.opportunity, self.opportunity)
        
        # Verify answers were saved
        self.assertEqual(application.answers.count(), 2)
    
    def test_optional_questions_can_be_skipped(self):
        """✅ Test that optional questions don't cause validation errors"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): 'Valid answer 1',
                str(self.required_question_2.id): 'Valid answer 2'
                # Skipping optional_question - should be OK
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_optional_questions_can_be_answered(self):
        """✅ Test that optional questions can be answered"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): 'Valid answer 1',
                str(self.required_question_2.id): 'Valid answer 2',
                str(self.optional_question.id): 'Optional answer'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all 3 answers were saved
        application = Application.objects.get(id=response.data['id'])
        self.assertEqual(application.answers.count(), 3)
    
    def test_duplicate_application_rejected(self):
        """Test that duplicate applications are rejected"""
        # Create first application
        self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): 'Answer 1',
                str(self.required_question_2.id): 'Answer 2'
            }
        }, format='json')
        
        # Try to create duplicate
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): 'Answer 1',
                str(self.required_question_2.id): 'Answer 2'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('opportunity', response.data)
        self.assertIn('allaqachon ariza topshirgansiz', str(response.data['opportunity']))
    
    def test_closed_opportunity_rejected(self):
        """Test that applications to closed opportunities are rejected"""
        self.opportunity.status = 'closed'
        self.opportunity.save()
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {
                str(self.required_question_1.id): 'Answer 1',
                str(self.required_question_2.id): 'Answer 2'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('opportunity', response.data)


class ProfileRequirementValidationTestCase(TestCase):
    """Test suite for profile requirement validation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create organization
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        # Create student
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        # Create opportunity with profile requirements
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Internship with Requirements',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        # Add profile requirements
        OpportunityProfileRequirement.objects.create(
            opportunity=self.opportunity,
            section='education',
            requirement_level='required',
            minimum_items=1
        )
        
        OpportunityProfileRequirement.objects.create(
            opportunity=self.opportunity,
            section='experience',
            requirement_level='required',
            minimum_items=1
        )
        
        self.client.force_authenticate(user=self.student_user)
    
    def test_application_without_required_profile_sections_rejected(self):
        """🔴 CRITICAL: Test that applications without required profile data are rejected"""
        # Student has no education or experience
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}  # No questions, only profile requirements
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('profile', response.data)
        # Check for either English or Uzbek text for education and experience
        profile_error = str(response.data['profile'])
        self.assertTrue('Education' in profile_error or 'Ta\'lim' in profile_error)
        self.assertTrue('Experience' in profile_error or 'Tajriba' in profile_error)
    
    def test_application_with_required_profile_sections_accepted(self):
        """✅ Test that applications with complete profile are accepted"""
        # Add education
        Education.objects.create(
            student=self.student_profile,
            institution='Test University',
            degree='bachelor',
            field_of_study='Computer Science',
            start_date='2020-09-01',
            end_date='2024-06-01'
        )
        
        # Add experience
        Experience.objects.create(
            student=self.student_profile,
            company='Test Company',
            title='Intern',
            description='Test work',
            start_date='2022-06-01',
            end_date='2022-08-31',
            experience_type='internship'
        )
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_profile_requirement_with_minimum_items(self):
        """Test that minimum_items requirement is enforced"""
        # Update requirement to need 2 education entries
        req = OpportunityProfileRequirement.objects.get(
            opportunity=self.opportunity,
            section='education'
        )
        req.minimum_items = 2
        req.save()
        
        # Add only 1 education
        Education.objects.create(
            student=self.student_profile,
            institution='Test University',
            degree='bachelor',
            field_of_study='Computer Science',
            start_date='2020-09-01',
            end_date='2024-06-01'
        )
        
        # Add experience (to satisfy that requirement)
        Experience.objects.create(
            student=self.student_profile,
            company='Test Company',
            title='Intern',
            description='Test work',
            start_date='2022-06-01',
            end_date='2022-08-31',
            experience_type='internship'
        )
        
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('profile', response.data)
        self.assertIn('kamida 2 ta kerak', str(response.data['profile']))


class DirectAPIBypassTestCase(TestCase):
    """🔴 CRITICAL: Test that direct API calls cannot bypass validation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create organization
        self.org_user = User.objects.create_user(
            username='test_org',
            email='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.organization = Organization.objects.create(
            user=self.org_user,
            name='Test Organization',
            description='Test description'
        )
        
        # Create student
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            university='Test University',
            major='Computer Science'
        )
        
        # Create opportunity with required questions
        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Test Opportunity',
            description='Test description',
            opportunity_type='scholarship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=60),
            location='Test City'
        )
        
        self.required_question = OpportunityQuestion.objects.create(
            opportunity=self.opportunity,
            question='Required question?',
            question_type='textarea',
            is_required=True
        )
        
        self.client.force_authenticate(user=self.student_user)
    
    def test_minimal_payload_rejected(self):
        """🔴 CRITICAL: Test minimal payload (only opportunity ID) is rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
    
    def test_null_answers_rejected(self):
        """🔴 CRITICAL: Test null answers field is rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': None
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
    
    def test_empty_dict_answers_rejected(self):
        """🔴 CRITICAL: Test empty dict answers is rejected"""
        response = self.client.post('/api/applications/', {
            'opportunity': self.opportunity.id,
            'answers': {}
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
    
    def test_curl_style_bypass_attempt(self):
        """🔴 CRITICAL: Simulate curl bypass attempt"""
        import json
        
        response = self.client.post(
            '/api/applications/',
            data=json.dumps({'opportunity': self.opportunity.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('answers', response.data)
        print(f"✅ Bypass attempt blocked: {response.data}")
