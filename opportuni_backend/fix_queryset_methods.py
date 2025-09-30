#!/usr/bin/env python3
"""
Script to fix all get_queryset methods by adding swagger_fake_view checks.
"""

import re
import os

def fix_queryset_method(content, model_name):
    """Fix a get_queryset method by adding swagger_fake_view check."""
    pattern = r'(def get_queryset\(self\):\s*\n)(.*?)(student_profile.*?\n.*?return\s+' + model_name + r'\.objects\.filter.*?\))'
    
    def replacement(match):
        method_def = match.group(1)
        existing_content = match.group(2)
        main_logic = match.group(3)
        
        # Skip if already has swagger_fake_view check
        if 'swagger_fake_view' in existing_content:
            return match.group(0)
        
        new_content = f"""{method_def}        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return {model_name}.objects.none()
            
        {main_logic}"""
        
        return new_content
    
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def fix_simple_queryset_method(content, model_name):
    """Fix simple queryset methods that directly filter."""
    pattern = rf'(def get_queryset\(self\):\s*\n)(.*?)(return\s+{model_name}\.objects\.filter.*?\))'
    
    def replacement(match):
        method_def = match.group(1)
        existing_content = match.group(2)
        return_statement = match.group(3)
        
        # Skip if already has swagger_fake_view check
        if 'swagger_fake_view' in existing_content:
            return match.group(0)
        
        new_content = f"""{method_def}        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return {model_name}.objects.none()
            
        {return_statement}"""
        
        return new_content
    
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def fix_file(file_path):
    """Fix all queryset methods in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # List of models that appear in queryset methods
    models = [
        'Education', 'Experience', 'StudentSkill', 'Project', 
        'Achievement', 'Language', 'SocialLink', 'StudentExamScore',
        'Organization', 'OrganizationMember', 'Opportunity',
        'Notification', 'Message', 'EmailTemplate'
    ]
    
    for model in models:
        content = fix_queryset_method(content, model)
        content = fix_simple_queryset_method(content, model)
    
    # Special case for user-based filters
    content = re.sub(
        r'(def get_queryset\(self\):\s*\n)(.*?)(return\s+.*?\.objects\.filter.*?recipient=self\.request\.user.*?\))',
        lambda m: f"{m.group(1)}        # Handle schema generation\n        if getattr(self, 'swagger_fake_view', False):\n            return {m.group(3).split('.')[0]}.objects.none()\n            \n        {m.group(3)}" if 'swagger_fake_view' not in m.group(2) else m.group(0),
        content,
        flags=re.DOTALL
    )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

# Fix all relevant files
files_to_fix = [
    'apps/students/views.py',
    'apps/organizations/views.py', 
    'apps/opportunities/views.py'
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        fix_file(file_path)