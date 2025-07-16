from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Organization(models.Model):
    ORGANIZATION_TYPES = (
        ('education', 'Education'),
        ('volunteering', 'Volunteering'),
        ('competition', 'Competition'),
        ('scholarship', 'Scholarship'),
        ('nonprofit', 'Non-profit'),
        ('government', 'Government'),
        ('corporation', 'Corporation'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES)
    description = models.TextField()
    logo = models.ImageField(upload_to='org_logos/', blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    
    # Location
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    
    # Social Media
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    ROLES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('recruiter', 'Recruiter'),
        ('viewer', 'Viewer'),
    )
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('organization', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"
