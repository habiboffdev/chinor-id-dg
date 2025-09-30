#!/usr/bin/env python3
"""
Script to add @extend_schema decorators to all function-based API views.
"""

import re

# Define schema decorators for each function based on the error output and function names
SCHEMA_DECORATORS = {
    # Accounts app
    'logout_view': '''@extend_schema(
    operation_id='logout_user',
    description='Logout user and blacklist token',
    responses={
        200: OpenApiResponse(description='Successfully logged out'),
        400: OpenApiResponse(description='Invalid token'),
    }
)''',
    
    'telegram_auth': '''@extend_schema(
    operation_id='telegram_auth',
    description='Authenticate user with Telegram',
    responses={
        200: OpenApiResponse(description='Authentication successful'),
        400: OpenApiResponse(description='Invalid Telegram data'),
    }
)''',
    
    'telegram_config': '''@extend_schema(
    operation_id='get_telegram_config',
    description='Get Telegram configuration',
    responses={
        200: OpenApiResponse(description='Telegram configuration'),
    }
)''',

    # Applications app (some already done)
    'check_application_status': '''@extend_schema(
    operation_id='check_application_status',
    description='Check application status for opportunity',
    responses={
        200: OpenApiResponse(description='Application status'),
        404: OpenApiResponse(description='No application found'),
    }
)''',
    
    'upload_application_document': '''@extend_schema(
    operation_id='upload_application_document',
    description='Upload document for application',
    responses={
        201: OpenApiResponse(description='Document uploaded successfully'),
        400: OpenApiResponse(description='Invalid file or application'),
    }
)''',

    # Communications app
    'mark_message_as_read': '''@extend_schema(
    operation_id='mark_message_as_read',
    description='Mark message as read',
    responses={
        200: OpenApiResponse(description='Message marked as read'),
        404: OpenApiResponse(description='Message not found'),
    }
)''',
    
    'send_bulk_email': '''@extend_schema(
    operation_id='send_bulk_email',
    description='Send bulk email to students',
    responses={
        200: OpenApiResponse(description='Emails sent successfully'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)''',

    # Notifications app
    'delete_notification': '''@extend_schema(
    operation_id='delete_notification',
    description='Delete notification',
    responses={
        204: OpenApiResponse(description='Notification deleted'),
        404: OpenApiResponse(description='Notification not found'),
    }
)''',
    
    'mark_notification_as_read': '''@extend_schema(
    operation_id='mark_notification_as_read',
    description='Mark notification as read',
    responses={
        200: OpenApiResponse(description='Notification marked as read'),
        404: OpenApiResponse(description='Notification not found'),
    }
)''',
    
    'mark_all_notifications_as_read': '''@extend_schema(
    operation_id='mark_all_notifications_as_read',
    description='Mark all notifications as read',
    responses={
        200: OpenApiResponse(description='All notifications marked as read'),
    }
)''',
    
    'notification_stats': '''@extend_schema(
    operation_id='get_notification_stats',
    description='Get notification statistics',
    responses={
        200: OpenApiResponse(description='Notification statistics'),
    }
)''',

    # Opportunities app
    'close_opportunity': '''@extend_schema(
    operation_id='close_opportunity',
    description='Close opportunity for applications',
    responses={
        200: OpenApiResponse(description='Opportunity closed successfully'),
        403: OpenApiResponse(description='Only organization owners allowed'),
        404: OpenApiResponse(description='Opportunity not found'),
    }
)''',
    
    'publish_opportunity': '''@extend_schema(
    operation_id='publish_opportunity',
    description='Publish opportunity to Telegram channel',
    responses={
        200: OpenApiResponse(description='Opportunity published successfully'),
        403: OpenApiResponse(description='Only organization owners allowed'),
        404: OpenApiResponse(description='Opportunity not found'),
    }
)''',
    
    'debug_opportunities': '''@extend_schema(
    operation_id='debug_opportunities',
    description='Debug opportunity data',
    responses={
        200: OpenApiResponse(description='Debug information'),
    }
)''',
    
    'opportunity_stats': '''@extend_schema(
    operation_id='get_opportunity_stats',
    description='Get opportunity statistics',
    responses={
        200: OpenApiResponse(description='Opportunity statistics'),
    }
)''',

    # Organizations app
    'invite_member': '''@extend_schema(
    operation_id='invite_organization_member',
    description='Invite member to organization',
    responses={
        200: OpenApiResponse(description='Member invited successfully'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)''',
    
    'get_students': '''@extend_schema(
    operation_id='get_students_list',
    description='Get list of students for organization',
    responses={
        200: OpenApiResponse(description='Students list'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)''',
    
    'invite_students': '''@extend_schema(
    operation_id='invite_students',
    description='Invite students to apply',
    responses={
        200: OpenApiResponse(description='Students invited successfully'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)''',
    
    'get_student_stats': '''@extend_schema(
    operation_id='get_student_statistics',
    description='Get student statistics for organization',
    responses={
        200: OpenApiResponse(description='Student statistics'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)''',
    
    'upload_logo': '''@extend_schema(
    operation_id='upload_organization_logo',
    description='Upload organization logo',
    responses={
        200: OpenApiResponse(description='Logo uploaded successfully'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)''',

    # Students app
    'student_application_stats': '''@extend_schema(
    operation_id='get_student_application_stats',
    description='Get student application statistics',
    responses={
        200: OpenApiResponse(description='Application statistics'),
        403: OpenApiResponse(description='Only students allowed'),
    }
)''',
    
    'public_opportuni_card': '''@extend_schema(
    operation_id='get_public_student_card',
    description='Get public student profile card',
    responses={
        200: OpenApiResponse(description='Student card data'),
        404: OpenApiResponse(description='Student not found'),
    }
)''',
    
    'seed_default_exams': '''@extend_schema(
    operation_id='seed_default_exams',
    description='Seed default academic exams',
    responses={
        200: OpenApiResponse(description='Default exams seeded'),
    }
)''',
    
    'upsert_social_link': '''@extend_schema(
    operation_id='upsert_social_link',
    description='Create or update social link',
    responses={
        200: OpenApiResponse(description='Social link updated'),
        201: OpenApiResponse(description='Social link created'),
    }
)''',
    
    'upload_profile_picture': '''@extend_schema(
    operation_id='upload_student_profile_picture',
    description='Upload student profile picture',
    responses={
        200: OpenApiResponse(description='Profile picture uploaded'),
        400: OpenApiResponse(description='Invalid file'),
    }
)''',
    
    'upload_resume': '''@extend_schema(
    operation_id='upload_student_resume',
    description='Upload student resume',
    responses={
        200: OpenApiResponse(description='Resume uploaded successfully'),
        400: OpenApiResponse(description='Invalid file'),
    }
)''',
}

def add_schema_decorators_to_file(file_path):
    """Add schema decorators to all function-based views in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Check if imports are already present
    if 'from drf_spectacular.utils import extend_schema, OpenApiResponse' not in content:
        # Add imports after other REST framework imports
        import_pattern = r'(from rest_framework[^\n]*\n)'
        if 'from drf_spectacular.utils import' not in content:
            content = re.sub(
                import_pattern,
                r'\1from drf_spectacular.utils import extend_schema, OpenApiResponse\n',
                content,
                count=1
            )
    
    # Add decorators to functions
    for func_name, decorator in SCHEMA_DECORATORS.items():
        # Pattern to match @api_view decorator followed by @permission_classes and function def
        pattern = rf'(@api_view\[.*?\]\s*\n)(@permission_classes\[.*?\]\s*\n)(def {func_name}\(.*?\):)'
        
        # Check if decorator already exists
        if f'operation_id=\'{func_name}\'' not in content and f'operation_id="{func_name}"' not in content:
            replacement = rf'{decorator}\n\1\2\3'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Added schema decorators to: {file_path}")
    else:
        print(f"No changes needed in: {file_path}")

# Apply to all view files
view_files = [
    'apps/accounts/views.py',
    'apps/applications/views.py', 
    'apps/communications/views.py',
    'apps/notifications/views.py',
    'apps/opportunities/views.py',
    'apps/organizations/views.py',
    'apps/students/views.py',
]

for file_path in view_files:
    add_schema_decorators_to_file(file_path)