from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('application_status', 'Application Status Update'),
        ('new_opportunity', 'New Opportunity'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('message_received', 'Message Received'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('system_announcement', 'System Announcement'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)  # Additional notification data
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    application_updates = models.BooleanField(default=True)
    new_opportunities = models.BooleanField(default=True)
    deadline_reminders = models.BooleanField(default=True)
    messages = models.BooleanField(default=True)
    system_announcements = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification settings for {self.user.username}"
