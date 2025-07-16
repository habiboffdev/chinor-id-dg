from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()


class EmailTemplate(models.Model):
    TEMPLATE_TYPES = (
        ('application_received', 'Application Received'),
        ('interview_invitation', 'Interview Invitation'),
        ('acceptance_letter', 'Acceptance Letter'),
        ('rejection_letter', 'Rejection Letter'),
        ('reminder', 'Reminder'),
        ('welcome', 'Welcome'),
        ('custom', 'Custom'),
    )
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='email_templates')
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    variables = models.JSONField(default=list)  # Available template variables
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Link to application or opportunity
    application = models.ForeignKey(
        'applications.Application', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='messages'
    )
    opportunity = models.ForeignKey(
        'opportunities.Opportunity', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='messages'
    )

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.subject}"


class BulkEmail(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='bulk_emails')
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    recipients = models.JSONField()  # List of recipient IDs
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sending', 'Sending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.organization.name} - {self.subject} ({self.sent_count} sent)"


class EmailLog(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    sender_organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    template_used = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    bulk_email = models.ForeignKey(BulkEmail, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.recipient.email}: {self.subject}"


class MessageThread(models.Model):
    """
    Groups related messages together
    """
    participants = models.ManyToManyField(User, related_name='message_threads')
    subject = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: Link to application or opportunity
    application = models.ForeignKey(
        'applications.Application', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='message_threads'
    )
    opportunity = models.ForeignKey(
        'opportunities.Opportunity', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='message_threads'
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Thread: {self.subject}"
