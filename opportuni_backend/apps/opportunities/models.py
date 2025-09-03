from django.db import models
from apps.organizations.models import Organization
from apps.students.models import Skill


class Opportunity(models.Model):
    OPPORTUNITY_TYPES = (
        ('internship', 'Internship'),
        ('volunteer', 'Volunteer'),
        ('competition', 'Competition'),
        ('scholarship', 'Scholarship'),
        ('job', 'Job'),
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
        ('event', 'Event'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=200)
    description = models.TextField()
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    application_deadline = models.DateTimeField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Requirements
    required_skills = models.ManyToManyField(Skill, blank=True)
    min_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    required_major = models.CharField(max_length=100, blank=True)
    graduation_year_min = models.IntegerField(null=True, blank=True)
    graduation_year_max = models.IntegerField(null=True, blank=True)
    age_min = models.IntegerField(null=True, blank=True)
    age_max = models.IntegerField(null=True, blank=True)
    # Details
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    compensation = models.CharField(max_length=100, blank=True)
    benefits = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='opportunity_covers/', blank=True, null=True)
    
    # Meta
    max_applications = models.IntegerField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.organization.name}"

    @property
    def application_count(self):
        return self.applications.count()

    @property
    def is_deadline_passed(self):
        from django.utils import timezone
        return timezone.now() > self.application_deadline

    @property
    def can_apply(self):
        if self.status != 'published':
            return False
        if self.is_deadline_passed:
            return False
        if self.max_applications and self.application_count >= self.max_applications:
            return False
        return True


class OpportunityRequirement(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='requirements')
    requirement = models.CharField(max_length=200)
    is_mandatory = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.opportunity.title} - {self.requirement}"


class OpportunityCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Opportunity Categories'

    def __str__(self):
        return self.name


class OpportunityQuestion(models.Model):
    QUESTION_TYPES = (
        ('text', 'Short Text'),
        ('textarea', 'Long Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('date', 'Date'),
        ('file', 'File Upload'),
        ('select', 'Multiple Choice'),
        ('checkbox', 'Checkbox'),
    )
    
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='additional_questions')
    question = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='text')
    is_required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=200, blank=True)
    help_text = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    
    # For select/checkbox options (JSON field)
    options = models.JSONField(blank=True, null=True, help_text="Options for select/checkbox questions")
    
    # Validation
    max_length = models.IntegerField(null=True, blank=True, help_text="Maximum length for text fields")
    min_length = models.IntegerField(null=True, blank=True, help_text="Minimum length for text fields")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.opportunity.title} - {self.question[:50]}"
