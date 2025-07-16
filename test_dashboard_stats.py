#!/usr/bin/env python
"""
Test script to check dashboard stats functionality
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

# Now import the models and test
from apps.students.models import StudentProfile
from apps.applications.models import Application
from apps.students.serializers import StudentDashboardSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def test_dashboard_stats():
    print("Testing Dashboard Stats Functionality")
    print("=" * 50)
    
    # Check if we have any users
    users = User.objects.filter(user_type='student')
    print(f"Found {users.count()} student users")
    
    if users.exists():
        user = users.first()
        print(f"Testing with user: {user.email}")
        
        # Get or create student profile
        try:
            student_profile = StudentProfile.objects.get(user=user)
            print(f"Found student profile for: {student_profile.user.get_full_name()}")
        except StudentProfile.DoesNotExist:
            print("No student profile found, creating one...")
            student_profile = StudentProfile.objects.create(user=user)
        
        # Check applications
        applications = Application.objects.filter(student=student_profile)
        print(f"Found {applications.count()} applications for this student")
        
        if applications.exists():
            print("Application statuses:")
            for status_choice, status_label in Application.STATUS_CHOICES:
                count = applications.filter(status=status_choice).count()
                print(f"  {status_label}: {count}")
        
        # Test the serializer
        print("\nTesting StudentDashboardSerializer:")
        serializer = StudentDashboardSerializer(student_profile)
        data = serializer.data
        
        print("Dashboard data:")
        for key, value in data.items():
            print(f"  {key}: {value}")
            
    else:
        print("No student users found. Creating sample data...")
        
        # Create a test user
        user = User.objects.create_user(
            email='test_student@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            user_type='student'
        )
        
        # Create student profile
        student_profile = StudentProfile.objects.create(
            user=user,
            university='Test University',
            major='Computer Science',
            graduation_year=2024
        )
        
        print(f"Created test student: {user.get_full_name()}")
        print("Now testing serializer with no applications:")
        
        serializer = StudentDashboardSerializer(student_profile)
        data = serializer.data
        
        print("Dashboard data:")
        for key, value in data.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    test_dashboard_stats()
