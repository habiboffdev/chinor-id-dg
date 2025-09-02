from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('ru', 'Русский'),
        ('uz', "O‘zbekcha"),
    )
    USER_TYPES = (
        ('student', 'Student'),
        ('organization', 'Organization'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    # Telegram linkage for bot onboarding/auth
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True, db_index=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override email to be required and unique
    email = models.EmailField(unique=True)
    
    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.user.email} Profile"
