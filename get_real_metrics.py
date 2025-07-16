#!/usr/bin/env python
"""
Real metrics tracker for Opportuni MVP
This script provides real statistics instead of fake numbers
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

from django.contrib.auth import get_user_model
from apps.students.models import StudentProfile
from apps.organizations.models import Organization
from apps.opportunities.models import Opportunity
from apps.applications.models import Application

User = get_user_model()

def get_real_metrics():
    """Get actual platform metrics for honest display"""
    
    print("Opportuni MVP - Real Platform Metrics")
    print("=" * 50)
    
    # User metrics
    total_users = User.objects.count()
    student_users = User.objects.filter(user_type='student').count()
    org_users = User.objects.filter(user_type='organization').count()
    
    # Profile completion
    student_profiles = StudentProfile.objects.count()
    org_profiles = Organization.objects.count()
    
    # Content metrics
    total_opportunities = Opportunity.objects.count()
    active_opportunities = Opportunity.objects.filter(status='active').count()
    
    # Application metrics
    total_applications = Application.objects.count()
    
    print(f"👥 Users:")
    print(f"   Total Users: {total_users}")
    print(f"   Students: {student_users}")
    print(f"   Organizations: {org_users}")
    print()
    
    print(f"📝 Profiles:")
    print(f"   Student Profiles: {student_profiles}")
    print(f"   Organization Profiles: {org_profiles}")
    print()
    
    print(f"🎯 Opportunities:")
    print(f"   Total Posted: {total_opportunities}")
    print(f"   Currently Active: {active_opportunities}")
    print()
    
    print(f"📋 Applications:")
    print(f"   Total Applications: {total_applications}")
    print()
    
    # Honest metrics for frontend
    print("Frontend Metrics (use these instead of fake numbers):")
    print("-" * 50)
    
    if student_users > 0:
        print(f"✅ {student_users} Early Access Students")
    else:
        print("🚀 Building Our Student Community")
        
    if org_users > 0:
        print(f"✅ {org_users} Partner Organizations")
    else:
        print("🤝 Seeking Organization Partners")
        
    if total_opportunities > 0:
        print(f"✅ {total_opportunities} Opportunities Available")
    else:
        print("💡 Curating Quality Opportunities")
    
    print()
    print("💡 MVP Status Suggestions for Landing Page:")
    print("-" * 50)
    
    if total_users < 10:
        print("• 'MVP Launch - Join the Foundation'")
        print("• 'Early Access - Shape the Future'")
        print("• 'Building Together - Your Input Matters'")
    elif total_users < 50:
        print("• 'Growing Community - Join Early Adopters'")
        print("• 'Beta Testing - Real Students, Real Feedback'")
    else:
        print("• Show real numbers with pride!")
        print(f"• '{student_users}+ Students Building Their Future'")
        print(f"• '{org_users}+ Organizations Finding Talent'")

def generate_honest_landing_stats():
    """Generate honest statistics for the landing page"""
    
    student_count = User.objects.filter(user_type='student').count()
    org_count = User.objects.filter(user_type='organization').count()
    opp_count = Opportunity.objects.count()
    
    # Create honest metrics
    if student_count == 0:
        student_text = "Building Community"
        student_icon = "🚀"
    elif student_count < 10:
        student_text = f"{student_count} Early Adopters"
        student_icon = "👥"
    else:
        student_text = f"{student_count}+ Students"
        student_icon = "🎓"
    
    if org_count == 0:
        org_text = "Seeking Partners"
        org_icon = "🤝"
    elif org_count < 5:
        org_text = f"{org_count} Partners"
        org_icon = "🏢"
    else:
        org_text = f"{org_count}+ Organizations"
        org_icon = "🏢"
    
    if opp_count == 0:
        opp_text = "Curating Opportunities"
        opp_icon = "💡"
    elif opp_count < 10:
        opp_text = f"{opp_count} Opportunities"
        opp_icon = "⭐"
    else:
        opp_text = f"{opp_count}+ Opportunities"
        opp_icon = "🎯"
    
    print("\nHTML Code for Honest Landing Page Stats:")
    print("=" * 50)
    print(f"""
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 pt-8">
        <div class="text-center">
            <div class="text-3xl font-bold text-primary-600">{student_icon}</div>
            <div class="text-gray-600 font-medium">{student_text}</div>
            <div class="text-sm text-gray-500 mt-1">Growing daily</div>
        </div>
        <div class="text-center">
            <div class="text-3xl font-bold text-secondary-600">{org_icon}</div>
            <div class="text-gray-600 font-medium">{org_text}</div>
            <div class="text-sm text-gray-500 mt-1">Quality focused</div>
        </div>
        <div class="text-center">
            <div class="text-3xl font-bold text-accent-600">{opp_icon}</div>
            <div class="text-gray-600 font-medium">{opp_text}</div>
            <div class="text-sm text-gray-500 mt-1">Hand-picked quality</div>
        </div>
    </div>
    """)

if __name__ == "__main__":
    get_real_metrics()
    print()
    generate_honest_landing_stats()
