#!/usr/bin/env python3
"""
Script to add @extend_schema_field decorators to all SerializerMethodField functions.
"""

import re
import os

# Map function names to their return types based on their purpose
FIELD_TYPE_MAPPING = {
    # Count/number functions
    'get_member_count': 'serializers.IntegerField',
    'get_opportunity_count': 'serializers.IntegerField', 
    'get_total_opportunities': 'serializers.IntegerField',
    'get_total_applications': 'serializers.IntegerField',
    'get_pending_applications': 'serializers.IntegerField',
    'get_accepted_applications': 'serializers.IntegerField',
    'get_rejected_applications': 'serializers.IntegerField',
    'get_interviews_scheduled': 'serializers.IntegerField',
    'get_unread_count': 'serializers.IntegerField',
    'get_days_since_applied': 'serializers.IntegerField',
    'get_days_until_deadline': 'serializers.IntegerField',
    'get_profile_completion': 'serializers.IntegerField',
    
    # Boolean functions
    'can_apply': 'serializers.BooleanField',
    'is_deadline_passed': 'serializers.BooleanField',
    
    # String functions
    'get_participants_names': 'serializers.CharField',
    'application_count': 'serializers.CharField',  # This one seems to be returning a string in the current implementation
    
    # Complex object functions
    'get_last_message': 'serializers.DictField',
    'get_recent_applications': 'serializers.ListField',
}

def add_schema_fields_to_file(file_path):
    """Add @extend_schema_field decorators to all SerializerMethodField functions."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Check if imports are already present
    if 'from drf_spectacular.utils import extend_schema_field' not in content:
        # Add import
        if 'from rest_framework import serializers' in content:
            content = re.sub(
                r'(from rest_framework import serializers\s*\n)',
                r'\1from drf_spectacular.utils import extend_schema_field\n',
                content,
                count=1
            )
        elif 'from drf_spectacular.utils import' in content:
            # Add to existing import
            content = re.sub(
                r'(from drf_spectacular.utils import[^)]*?)(\))',
                r'\1, extend_schema_field\2',
                content
            )
    
    # Add decorators to method field functions
    for func_name, field_type in FIELD_TYPE_MAPPING.items():
        # Pattern to match function definition
        pattern = rf'(\s+)(def {func_name}\(self, obj\):)'
        
        # Check if decorator already exists
        if f'@extend_schema_field({field_type})' not in content:
            # Add decorator before function
            replacement = rf'\1@extend_schema_field({field_type})\n\1\2'
            content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Added schema field decorators to: {file_path}")
        
        # Count how many were added
        added_count = content.count('@extend_schema_field') - original_content.count('@extend_schema_field')
        print(f"  Added {added_count} field decorators")
    else:
        print(f"No changes needed in: {file_path}")

# Apply to all serializer files
serializer_files = [
    'apps/applications/serializers.py',
    'apps/communications/serializers.py', 
    'apps/opportunities/serializers.py',
    'apps/organizations/serializers.py',
    'apps/students/serializers.py',
]

for file_path in serializer_files:
    if os.path.exists(file_path):
        add_schema_fields_to_file(file_path)