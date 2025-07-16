from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@shared_task
def send_email_notification(recipient_email, subject, message, template_name=None, context=None):
    """
    Send email notification to a user.
    """
    try:
        if template_name and context:
            html_message = render_to_string(template_name, context)
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False


@shared_task
def send_bulk_emails(template_id, recipient_ids, subject, body):
    """
    Send bulk emails to multiple recipients.
    """
    from apps.communications.models import BulkEmail, EmailLog
    from apps.organizations.models import Organization
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        bulk_email = BulkEmail.objects.get(id=template_id)
        bulk_email.status = 'sending'
        bulk_email.save()
        
        sent_count = 0
        failed_count = 0
        
        for user_id in recipient_ids:
            try:
                user = User.objects.get(id=user_id)
                success = send_email_notification.delay(
                    user.email, subject, body
                ).get()
                
                # Log the email
                EmailLog.objects.create(
                    recipient=user,
                    sender_organization=bulk_email.organization,
                    subject=subject,
                    body=body,
                    template_used=bulk_email.template,
                    bulk_email=bulk_email,
                    delivered=success
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except User.DoesNotExist:
                failed_count += 1
        
        bulk_email.sent_count = sent_count
        bulk_email.failed_count = failed_count
        bulk_email.status = 'completed'
        bulk_email.save()
        
        logger.info(f"Bulk email completed: {sent_count} sent, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Bulk email task failed: {str(e)}")
        if 'bulk_email' in locals():
            bulk_email.status = 'failed'
            bulk_email.save()


@shared_task
def send_websocket_notification(user_id, notification_data):
    """
    Send real-time notification via WebSocket.
    """
    try:
        group_name = f"notifications_{user_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "data": notification_data
            }
        )
        logger.info(f"WebSocket notification sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send WebSocket notification: {str(e)}")


@shared_task
def deadline_reminder_task():
    """
    Check for upcoming deadlines and send reminders.
    """
    from apps.opportunities.models import Opportunity
    from apps.notifications.models import Notification
    from django.contrib.auth import get_user_model
    from datetime import timedelta
    
    User = get_user_model()
    
    try:
        # Get opportunities with deadlines in the next 24 hours
        tomorrow = timezone.now() + timedelta(days=1)
        upcoming_opportunities = Opportunity.objects.filter(
            status='published',
            application_deadline__lte=tomorrow,
            application_deadline__gt=timezone.now()
        )
        
        reminder_count = 0
        
        for opportunity in upcoming_opportunities:
            # Get users who haven't applied yet (this would need more complex logic)
            # For now, we'll send to all students
            students = User.objects.filter(user_type='student')
            
            for student in students:
                # Check if student has already applied
                if not opportunity.applications.filter(student__user=student).exists():
                    # Create notification
                    notification = Notification.objects.create(
                        recipient=student,
                        notification_type='deadline_reminder',
                        title=f"Deadline Reminder: {opportunity.title}",
                        message=f"The application deadline for {opportunity.title} is approaching. Apply now!",
                        data={
                            'opportunity_id': opportunity.id,
                            'deadline': opportunity.application_deadline.isoformat()
                        }
                    )
                    
                    # Send WebSocket notification
                    send_websocket_notification.delay(student.id, {
                        'id': notification.id,
                        'type': notification.notification_type,
                        'title': notification.title,
                        'message': notification.message,
                        'data': notification.data,
                        'created_at': notification.created_at.isoformat()
                    })
                    
                    reminder_count += 1
        
        logger.info(f"Sent {reminder_count} deadline reminders")
        
    except Exception as e:
        logger.error(f"Deadline reminder task failed: {str(e)}")


@shared_task
def cleanup_old_notifications():
    """
    Clean up old notifications (older than 30 days).
    """
    from apps.notifications.models import Notification
    from datetime import timedelta
    
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old notifications")
        
    except Exception as e:
        logger.error(f"Notification cleanup task failed: {str(e)}")


@shared_task
def generate_application_report(organization_id, report_type='monthly'):
    """
    Generate application reports for organizations.
    """
    from apps.organizations.models import Organization
    from apps.applications.models import Application
    from datetime import timedelta
    
    try:
        organization = Organization.objects.get(id=organization_id)
        
        if report_type == 'monthly':
            start_date = timezone.now() - timedelta(days=30)
        elif report_type == 'weekly':
            start_date = timezone.now() - timedelta(days=7)
        else:
            start_date = timezone.now() - timedelta(days=365)
        
        applications = Application.objects.filter(
            opportunity__organization=organization,
            applied_at__gte=start_date
        )
        
        report_data = {
            'total_applications': applications.count(),
            'pending_applications': applications.filter(status='pending').count(),
            'accepted_applications': applications.filter(status='accepted').count(),
            'rejected_applications': applications.filter(status='rejected').count(),
            'opportunities_with_applications': applications.values('opportunity').distinct().count(),
        }
        
        # Here you would save the report or send it via email
        logger.info(f"Generated {report_type} report for {organization.name}: {report_data}")
        
        return report_data
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return None
