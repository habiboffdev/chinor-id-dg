#!/usr/bin/env python3
"""
Script to fix the corrupted .*.objects.none() patterns in students views.
"""

import re

def fix_students_file():
    with open('apps/students/views.py', 'r') as f:
        content = f.read()
    
    # Map the correct model for each context
    replacements = [
        # Fix Experience views
        (r'(class Experience.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return Experience.objects.none()', re.DOTALL),
        (r'(# Experience.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return Experience.objects.none()', re.DOTALL),
        
        # Fix StudentSkill views  
        (r'(class.*?Skill.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return StudentSkill.objects.none()', re.DOTALL),
        
        # Fix Project views
        (r'(class Project.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return Project.objects.none()', re.DOTALL),
        
        # Fix Achievement views
        (r'(class Achievement.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return Achievement.objects.none()', re.DOTALL),
        
        # Fix Language views
        (r'(class Language.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return Language.objects.none()', re.DOTALL),
        
        # Fix SocialLink views
        (r'(class.*?Social.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return SocialLink.objects.none()', re.DOTALL),
        
        # Fix StudentExamScore views
        (r'(class.*?ExamScore.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return StudentExamScore.objects.none()', re.DOTALL),
        
        # Fix AcademicExamSection views
        (r'(exam_id = self\.kwargs.*?def get_queryset.*?)return \..*\.objects\.none\(\)', r'\1return AcademicExamSection.objects.none()', re.DOTALL),
    ]
    
    for pattern, replacement, flags in replacements:
        content = re.sub(pattern, replacement, content, flags=flags)
    
    # Generic fix for any remaining .*.objects.none() patterns based on context
    # Look for return Model.objects.filter patterns and use the same model
    def fix_generic_pattern(match):
        before = match.group(1)
        after = match.group(2)
        
        # Look for model name in the following return statement
        model_match = re.search(r'return\s+(\w+)\.objects\.filter', after)
        if model_match:
            model_name = model_match.group(1)
            return f"{before}return {model_name}.objects.none(){after}"
        
        # Default fallback
        return f"{before}return StudentProfile.objects.none(){after}"
    
    content = re.sub(
        r'(.*?return )\..*\.objects\.none\(\)(.*?return\s+\w+\.objects\.filter.*?)',
        fix_generic_pattern,
        content,
        flags=re.DOTALL
    )
    
    with open('apps/students/views.py', 'w') as f:
        f.write(content)
    
    print("Fixed students views")

if __name__ == "__main__":
    fix_students_file()