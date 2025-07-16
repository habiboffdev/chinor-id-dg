#!/usr/bin/env python
"""
Create multiple applications with different statuses for demonstration
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

def create_demo_applications():
    print("Creating demo applications with different statuses...")
    
    # Get the existing student user
    try:
        student_user = User.objects.get(email='habibov.mirzosharif@gmail.com')
        student_profile = StudentProfile.objects.get(user=student_user)
        print(f"Using existing student: {student_user.get_full_name()}")
    except (User.DoesNotExist, StudentProfile.DoesNotExist):
        print("Student not found!")
        return
    
    # Get existing opportunities
    opportunities = list(Opportunity.objects.all())
    print(f"Found {len(opportunities)} opportunities")
    
    # If we don't have enough opportunities, we'll create some basic ones
    demo_statuses = ['pending', 'under_review', 'accepted', 'rejected', 'pending']
    
    # Clear existing applications for clean demo
    existing_apps = Application.objects.filter(student=student_profile)
    print(f"Removing {existing_apps.count()} existing applications for clean demo")
    existing_apps.delete()
    
    # Create applications with different statuses
    for i, status in enumerate(demo_statuses):
        if i < len(opportunities):
            opportunity = opportunities[i]
            Application.objects.create(
                student=student_profile,
                opportunity=opportunity,
                status=status
            )
            print(f"Created application for '{opportunity.title}' with status '{status}'")
    
    # Show final stats
    print("\nDemo application statistics:")
    applications = Application.objects.filter(student=student_profile)
    print(f"Total applications: {applications.count()}")
    
    for status_choice, status_label in Application.STATUS_CHOICES:
        count = applications.filter(status=status_choice).count()
        if count > 0:
            print(f"{status_label}: {count}")

if __name__ == "__main__":
    create_demo_applications()
