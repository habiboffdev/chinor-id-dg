# API Documentation Analysis: Missing Endpoints Report

## Executive Summary

The OpenAPI schema generation shows **26 out of 27 function-based API endpoints are missing** from the documentation, despite being fully functional in the backend. This represents a significant gap in API documentation coverage.

## Current Schema Coverage

- **Total Documented Endpoints**: 80
- **Missing Function-Based Views**: 26
- **Documentation Coverage**: ~75% (estimated)

### Breakdown by App:
- **Students**: 27 endpoints documented, ~6 missing function-based views
- **Organizations**: 11 endpoints documented, ~5 missing function-based views  
- **Opportunities**: 10 endpoints documented, ~4 missing function-based views
- **Applications**: 10 endpoints documented, ~3 missing function-based views
- **Notifications**: 7 endpoints documented, ~4 missing function-based views
- **Communications**: 6 endpoints documented, ~2 missing function-based views
- **Auth**: 9 endpoints documented, ~3 missing function-based views

## 🚨 **Poorly Documented Endpoints (Missing from Schema)**

### Applications App
1. **`POST /api/applications/{id}/check-status/`** - Check application status
   - Function: `check_application_status`
   - Purpose: Check if user has applied to specific opportunity
   
2. **`POST /api/applications/upload-document/`** - Upload application document
   - Function: `upload_application_document` 
   - Purpose: Upload supporting documents for applications

### Authentication App
3. **`POST /api/auth/logout/`** - Logout user
   - Function: `logout_view`
   - Purpose: Logout user and blacklist JWT token
   
4. **`POST /api/auth/telegram/`** - Telegram authentication
   - Function: `telegram_auth`
   - Purpose: Authenticate via Telegram bot integration
   
5. **`GET /api/auth/telegram/config/`** - Telegram configuration
   - Function: `telegram_config`
   - Purpose: Get Telegram bot configuration

### Communications App
6. **`POST /api/communications/messages/{id}/read/`** - Mark message as read
   - Function: `mark_message_as_read`
   - Purpose: Mark specific message as read
   
7. **`POST /api/communications/send-bulk-email/`** - Send bulk email
   - Function: `send_bulk_email`
   - Purpose: Send bulk emails to students (organization feature)

### Notifications App
8. **`DELETE /api/notifications/{id}/`** - Delete notification
   - Function: `delete_notification`
   - Purpose: Delete specific notification
   
9. **`PUT /api/notifications/{id}/read/`** - Mark notification as read
   - Function: `mark_notification_as_read`
   - Purpose: Mark specific notification as read
   
10. **`PUT /api/notifications/mark-all-read/`** - Mark all notifications as read
    - Function: `mark_all_notifications_as_read`
    - Purpose: Mark all user notifications as read
    
11. **`GET /api/notifications/stats/`** - Notification statistics
    - Function: `notification_stats`
    - Purpose: Get notification statistics for user

### Opportunities App
12. **`POST /api/opportunities/{id}/close/`** - Close opportunity
    - Function: `close_opportunity`
    - Purpose: Close opportunity for new applications
    
13. **`POST /api/opportunities/{id}/publish/`** - Publish to Telegram
    - Function: `publish_opportunity`
    - Purpose: Publish opportunity to Telegram channel
    
14. **`GET /api/opportunities/debug/`** - Debug opportunities
    - Function: `debug_opportunities`
    - Purpose: Debug/troubleshoot opportunity data
    
15. **`GET /api/opportunities/stats/`** - Opportunity statistics
    - Function: `opportunity_stats`
    - Purpose: Get opportunity statistics

### Organizations App
16. **`POST /api/organizations/invite-member/`** - Invite organization member
    - Function: `invite_member`
    - Purpose: Invite new member to organization
    
17. **`GET /api/organizations/students/`** - Get students list
    - Function: `get_students`
    - Purpose: Get filtered list of students for organization
    
18. **`POST /api/organizations/invite-students/`** - Invite students
    - Function: `invite_students`
    - Purpose: Send invitations to students for opportunities
    
19. **`GET /api/organizations/student-stats/`** - Student statistics
    - Function: `get_student_stats`
    - Purpose: Get student application statistics
    
20. **`POST /api/organizations/upload-logo/`** - Upload organization logo
    - Function: `upload_logo`
    - Purpose: Upload organization logo image

### Students App
21. **`GET /api/students/application-stats/`** - Student application statistics
    - Function: `student_application_stats`
    - Purpose: Get detailed application statistics for student
    
22. **`GET /api/students/{id}/public-card/`** - Public student profile card
    - Function: `public_opportuni_card`
    - Purpose: Get public-facing student profile card
    
23. **`POST /api/students/seed-exams/`** - Seed default exams
    - Function: `seed_default_exams`
    - Purpose: Initialize default academic exam data
    
24. **`POST /api/students/social-links/`** - Create/update social link
    - Function: `upsert_social_link`
    - Purpose: Add or update student social media links
    
25. **`POST /api/students/upload-profile-picture/`** - Upload profile picture
    - Function: `upload_profile_picture`
    - Purpose: Upload student profile picture
    
26. **`POST /api/students/upload-resume/`** - Upload resume
    - Function: `upload_resume`
    - Purpose: Upload student resume/CV

## 🔍 **Root Cause Analysis**

The missing endpoints share these characteristics:
1. **Function-based views** using `@api_view` decorator
2. **Missing serializer_class** information for schema generation
3. **@extend_schema decorators present** but schema generator still can't infer serializers
4. **Complex request/response handling** that doesn't follow standard DRF patterns

## 📊 **Impact Assessment**

### High Priority Missing Endpoints:
- **File uploads**: `upload_resume`, `upload_profile_picture`, `upload_logo`, `upload_application_document`
- **Core actions**: `withdraw_application`, `close_opportunity`, `publish_opportunity`
- **User interactions**: `mark_notification_as_read`, `mark_message_as_read`

### Medium Priority Missing Endpoints:
- **Statistics**: `application_stats`, `opportunity_stats`, `notification_stats`
- **Member management**: `invite_member`, `invite_students`, `get_students`

### Low Priority Missing Endpoints:
- **Debug/Admin**: `debug_opportunities`, `seed_default_exams`, `telegram_config`

## 🛠️ **Recommended Fix Strategy**

1. **Convert to Class-Based Views** (Most Effective)
   - Refactor function-based views to use DRF generic views
   - Automatic serializer detection and proper schema generation
   
2. **Add Explicit Serializer Classes** (Moderate Effort)
   - Create specific serializers for each function's request/response
   - Add serializer_class attributes or use @extend_schema with explicit serializers
   
3. **Enhanced @extend_schema Decorators** (Quick Fix)
   - Add detailed request/response schemas to existing decorators
   - Specify exact input/output serializers

## 💡 **Next Steps**

1. **Immediate**: Fix the 6 highest-priority endpoints (file uploads + core actions)
2. **Short-term**: Address statistics and member management endpoints  
3. **Long-term**: Consider architectural improvements for better API documentation

The missing endpoints represent critical functionality that frontend developers need documented for proper integration.