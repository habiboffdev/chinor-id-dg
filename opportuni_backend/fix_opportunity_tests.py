#!/usr/bin/env python3

import re

def fix_opportunity_creation(file_path):
    """Fix Opportunity.objects.create calls to include start_date and valid opportunity_type"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Valid opportunity types from the model
    valid_types = ['conference', 'volunteer', 'international_events', 'scholarship', 'camp', 'grant', 'mentoring', 'academic_program']
    
    # Pattern to match Opportunity.objects.create calls
    pattern = r'(Opportunity\.objects\.create\([^)]+?)opportunity_type=[\'"]internship[\'"]([^)]+?)\)'
    
    def replacement(match):
        before = match.group(1)
        after = match.group(2)
        
        # Use academic_program as default replacement for internship
        new_type = 'academic_program'
        
        # Add start_date if not present
        if 'start_date=' not in after:
            # Find where to insert start_date (after application_deadline)
            if 'application_deadline=' in after:
                after = re.sub(
                    r'(application_deadline=[^,]+),',
                    r'\1,\n            start_date=timezone.now().date() + timedelta(days=7),',
                    after
                )
        
        return f"{before}opportunity_type='{new_type}'{after})"
    
    # Apply the replacement
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Also fix any remaining start_date issues for existing Opportunity.objects.create without start_date
    # This pattern looks for Opportunity.objects.create that doesn't have start_date
    pattern2 = r'(Opportunity\.objects\.create\([^)]*application_deadline=[^,]+,)([^)]*?)(\))'
    
    def add_start_date(match):
        before = match.group(1)
        middle = match.group(2)
        after = match.group(3)
        
        if 'start_date=' not in middle:
            middle = '\n            start_date=timezone.now().date() + timedelta(days=7),' + middle
        
        return f"{before}{middle}{after}"
    
    content = re.sub(pattern2, add_start_date, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

# Fix all test files
fix_opportunity_creation('apps/applications/tests.py')
fix_opportunity_creation('apps/communications/tests.py')

print("All Opportunity.objects.create calls have been fixed!")