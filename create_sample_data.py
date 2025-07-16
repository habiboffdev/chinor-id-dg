#!/usr/bin/env python3
"""
Create sample data for testing the profile page
"""

import os
import sys
import django
from datetime import date, datetime

# Add the project root to the Python path
sys.path.append('/home/mirzosharif/MVP/chinor_id_new/opportuni_backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.students.models import StudentProfile, Education, Experience, Skill, StudentSkill, Project, Achievement, Language

User = get_user_model()

def create_sample_data():
    """Create sample data for testing"""
    
    print("🔧 Creating sample data...")
    
    # Get the test user
    try:
        user = User.objects.get(email='test@example.com')
        profile = StudentProfile.objects.get(user=user)
        print(f"✅ Found test user and profile: {user.email}")
    except (User.DoesNotExist, StudentProfile.DoesNotExist):
        print("❌ Test user or profile not found")
        return False
    
    # Create sample skills first
    print("\n🛠️  Creating sample skills...")
    sample_skills = [
        ('Python', 'technical'),
        ('JavaScript', 'technical'),
        ('React', 'technical'),
        ('Django', 'technical'),
        ('Machine Learning', 'technical'),
        ('Communication', 'soft_skill'),
        ('Leadership', 'soft_skill'),
        ('Git', 'tool'),
        ('Docker', 'tool'),
        ('SQL', 'technical'),
    ]
    
    for skill_name, category in sample_skills:
        skill, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={'category': category}
        )
        if created:
            print(f"  ✅ Created skill: {skill_name}")
        else:
            print(f"  ℹ️  Skill already exists: {skill_name}")
    
    # Create sample education
    print("\n📚 Creating sample education...")
    if not Education.objects.filter(student=profile).exists():
        education = Education.objects.create(
            student=profile,
            institution="University of Technology",
            degree="bachelor",
            field_of_study="Computer Science",
            start_date=date(2020, 9, 1),
            end_date=date(2024, 5, 31),
            gpa=3.75,
            description="Bachelor's degree in Computer Science with focus on software engineering and AI."
        )
        print(f"  ✅ Created education: {education}")
    else:
        print("  ℹ️  Education already exists")
    
    # Create sample experience
    print("\n💼 Creating sample experience...")
    if not Experience.objects.filter(student=profile).exists():
        experience = Experience.objects.create(
            student=profile,
            title="Software Developer Intern",
            company="Tech Solutions Inc",
            experience_type="internship",
            description="Developed web applications using Python/Django and React. Worked on API integration and database optimization.",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 8, 31),
            location="San Francisco, CA"
        )
        print(f"  ✅ Created experience: {experience}")
    else:
        print("  ℹ️  Experience already exists")
    
    # Create sample student skills
    print("\n🎯 Creating sample student skills...")
    if not StudentSkill.objects.filter(student=profile).exists():
        python_skill = Skill.objects.get(name='Python')
        js_skill = Skill.objects.get(name='JavaScript')
        react_skill = Skill.objects.get(name='React')
        
        StudentSkill.objects.create(
            student=profile,
            skill=python_skill,
            proficiency_level=3,
            years_experience=2
        )
        StudentSkill.objects.create(
            student=profile,
            skill=js_skill,
            proficiency_level=3,
            years_experience=2
        )
        StudentSkill.objects.create(
            student=profile,
            skill=react_skill,
            proficiency_level=2,
            years_experience=1
        )
        print("  ✅ Created student skills")
    else:
        print("  ℹ️  Student skills already exist")
    
    # Create sample project
    print("\n🚀 Creating sample project...")
    if not Project.objects.filter(student=profile).exists():
        project = Project.objects.create(
            student=profile,
            title="E-commerce Platform",
            description="Full-stack e-commerce platform built with Django and React. Features include user authentication, product management, shopping cart, and payment integration.",
            project_url="https://github.com/user/ecommerce-platform",
            github_url="https://github.com/user/ecommerce-platform",
            start_date=date(2023, 3, 1),
            end_date=date(2023, 5, 31),
            featured=True
        )
        # Add technologies
        python_skill = Skill.objects.get(name='Python')
        js_skill = Skill.objects.get(name='JavaScript')
        project.technologies.add(python_skill, js_skill)
        print(f"  ✅ Created project: {project}")
    else:
        print("  ℹ️  Project already exists")
    
    # Create sample achievement
    print("\n🏆 Creating sample achievement...")
    if not Achievement.objects.filter(student=profile).exists():
        achievement = Achievement.objects.create(
            student=profile,
            title="Best Student Project Award",
            achievement_type="award",
            description="Received the best student project award for developing an innovative machine learning solution.",
            issuing_organization="University of Technology",
            date_achieved=date(2023, 5, 15),
            certificate_url="https://example.com/certificate"
        )
        print(f"  ✅ Created achievement: {achievement}")
    else:
        print("  ℹ️  Achievement already exists")
    
    # Create sample language
    print("\n🗣️  Creating sample language...")
    if not Language.objects.filter(student=profile).exists():
        Language.objects.create(
            student=profile,
            language="English",
            proficiency="native"
        )
        Language.objects.create(
            student=profile,
            language="Spanish",
            proficiency="professional_working"
        )
        print("  ✅ Created languages")
    else:
        print("  ℹ️  Languages already exist")
    
    print("\n✅ Sample data creation completed!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 SAMPLE DATA CREATION")
    print("=" * 60)
    
    success = create_sample_data()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Sample data created successfully!")
        print("🌐 You can now test the profile page at: http://localhost:8080/profile.html")
    else:
        print("❌ Sample data creation failed!")
    print("=" * 60)
