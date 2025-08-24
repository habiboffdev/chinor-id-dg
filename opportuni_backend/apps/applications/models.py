from django.db import models
from django.contrib.auth import get_user_model
from apps.students.models import StudentProfile
from apps.opportunities.models import Opportunity

User = get_user_model()


class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Application Data - Now fully dynamic via ApplicationAnswer model
    additional_documents = models.JSONField(default=list)  # Store file URLs
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Review Data
    reviewer_notes = models.TextField(blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('student', 'opportunity')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.opportunity.title}"


class ApplicationDocument(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='application_docs/')
    document_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application} - {self.document_type}"


class ApplicationNote(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    is_internal = models.BooleanField(default=True)  # Internal org notes vs student-visible
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.author.username} on {self.application}"


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.application} - {self.old_status} to {self.new_status}"


class ApplicationAnswer(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('opportunities.OpportunityQuestion', on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    answer_file = models.FileField(upload_to='application_answers/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('application', 'question')
    
    def __str__(self):
        return f"{self.application} - {self.question.question[:30]}"
