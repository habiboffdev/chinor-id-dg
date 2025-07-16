#!/usr/bin/env python
"""
Add more sample applications to existing user for testing
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
from django.contrib.auth import get_user_model

User = get_user_model()

def add_more_applications():
    print("Adding more sample applications...")
    
    # Get the existing student user
    try:
        student_user = User.objects.get(email='habibov.mirzosharif@gmail.com')
        student_profile = StudentProfile.objects.get(user=student_user)
        print(f"Using existing student: {student_user.get_full_name()}")
    except (User.DoesNotExist, StudentProfile.DoesNotExist):
        print("Student not found!")
        return
    
    # Get available opportunities (we'll create fake applications by changing existing ones or creating new records)
    opportunities = Opportunity.objects.all()[:5]  # Get some opportunities
    
    if not opportunities.exists():
        print("No opportunities found. Cannot create applications.")
        return
    
    # Define test statuses to create
    test_statuses = ['pending', 'under_review', 'accepted', 'rejected']
    
    existing_apps = Application.objects.filter(student=student_profile)
    print(f"Found {existing_apps.count()} existing applications")
    
    # Add new applications or update existing ones
    for i, status in enumerate(test_statuses):
        if i < len(opportunities):
            opportunity = opportunities[i]
            
            # Check if application already exists for this opportunity
            app, created = Application.objects.get_or_create(
                student=student_profile,
                opportunity=opportunity,
                defaults={'status': status}
            )
            
            if not created and app.status != status:
                # Update the status if it exists but has different status
                old_status = app.status
                app.status = status
                app.save()
                print(f"Updated application for '{opportunity.title}' from '{old_status}' to '{status}'")
            elif created:
                print(f"Created new application for '{opportunity.title}' with status '{status}'")
            else:
                print(f"Application for '{opportunity.title}' already exists with status '{app.status}'")
    
    # Show final stats
    print("\nFinal application statistics:")
    applications = Application.objects.filter(student=student_profile)
    print(f"Total applications: {applications.count()}")
    
    for status_choice, status_label in Application.STATUS_CHOICES:
        count = applications.filter(status=status_choice).count()
        if count > 0:
            print(f"{status_label}: {count}")

if __name__ == "__main__":
    add_more_applications()
