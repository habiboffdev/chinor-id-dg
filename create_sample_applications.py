#!/usr/bin/env python
"""
Create sample application data for testing dashboard statistics
"""

import os
import sys
import django
from pathlib import Path

# Add the Django project to the Python path
project_root = Path(__file__).parent / 'opportuni_backend'
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()

from apps.students.models import StudentProfile
from apps.applications.models import Application
from apps.opportunities.models import Opportunity
from apps.organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

def create_sample_applications():
    print("Creating sample application data...")
    
    # Get or create test student
    student_user, created = User.objects.get_or_create(
        email='test_student@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Student',
            'user_type': 'student'
        }
    )
    
    if created:
        student_user.set_password('testpass123')
        student_user.save()
        print(f"Created new student user: {student_user.email}")
    else:
        print(f"Using existing student user: {student_user.email}")
    
    # Get or create student profile
    student_profile, created = StudentProfile.objects.get_or_create(
        user=student_user,
        defaults={
            'university': 'Test University',
            'major': 'Computer Science',
            'graduation_year': 2024
        }
    )
    
    # Get existing organizations and opportunities
    opportunities = Opportunity.objects.all()[:5]  # Get first 5 opportunities
    
    if not opportunities.exists():
        print("No opportunities found. Creating a sample opportunity...")
        
        # Create a test organization first
        org_user, created = User.objects.get_or_create(
            email='test_org@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Organization',
                'user_type': 'organization'
            }
        )
        
        if created:
            org_user.set_password('testpass123')
            org_user.save()
        
        organization, created = Organization.objects.get_or_create(
            user=org_user,
            defaults={
                'name': 'Test Organization',
                'industry': 'Technology',
                'description': 'A test organization for demo purposes'
            }
        )
        
        # Create a test opportunity
        opportunity = Opportunity.objects.create(
            title='Software Developer Internship',
            description='A great internship opportunity for students',
            organization=organization,
            location='Remote',
            opportunity_type='internship',
            application_deadline='2024-12-31',
            status='active'
        )
        opportunities = [opportunity]
        print("Created sample opportunity")
    
    # Create sample applications with different statuses
    statuses = ['pending', 'under_review', 'accepted', 'rejected', 'pending']
    
    for i, opportunity in enumerate(opportunities[:5]):
        status = statuses[i % len(statuses)]
        
        # Check if application already exists
        application, created = Application.objects.get_or_create(
            student=student_profile,
            opportunity=opportunity,
            defaults={'status': status}
        )
        
        if created:
            print(f"Created application for '{opportunity.title}' with status '{status}'")
        else:
            print(f"Application already exists for '{opportunity.title}' with status '{application.status}'")
    
    # Print final statistics
    print("\nFinal statistics:")
    applications = Application.objects.filter(student=student_profile)
    print(f"Total applications: {applications.count()}")
    
    for status_choice, status_label in Application.STATUS_CHOICES:
        count = applications.filter(status=status_choice).count()
        if count > 0:
            print(f"{status_label}: {count}")

if __name__ == "__main__":
    create_sample_applications()
