from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Personal Information
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    
    # Academic Information
    university = models.CharField(max_length=200, blank=True)
    major = models.CharField(max_length=100, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Files and URLs
    resume = models.FileField(upload_to='resumes/', blank=True)
    portfolio_url = models.URLField(blank=True)
    about_me = models.TextField(blank=True)
    
    # Contact preferences
    phone_visible = models.BooleanField(default=False)
    email_visible = models.BooleanField(default=True)
    
    # Profile completion
    profile_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - Student Profile"
    
    def save(self, *args, **kwargs):
        # Auto-generate student ID if not provided
        if not self.student_id:
            self.student_id = f"STU{self.user.id:06d}"
        super().save(*args, **kwargs)

class Education(models.Model):
    DEGREE_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD'),
        ('certificate', 'Certificate'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} at {self.institution}"

class Experience(models.Model):
    EXPERIENCE_TYPES = [
        ('internship', 'Internship'),
        ('part_time', 'Part-time'),
        ('full_time', 'Full-time'),
        ('volunteer', 'Volunteer'),
        ('freelance', 'Freelance'),
        ('project', 'Project'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=200)
    experience_type = models.CharField(max_length=20, choices=EXPERIENCE_TYPES)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} at {self.company}"

class Skill(models.Model):
    SKILL_CATEGORIES = [
        ('technical', 'Technical'),
        ('language', 'Language'),
        ('soft_skill', 'Soft Skill'),
        ('tool', 'Tool/Software'),
        ('certification', 'Certification'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class StudentSkill(models.Model):
    PROFICIENCY_LEVELS = [
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.IntegerField(choices=PROFICIENCY_LEVELS)
    years_experience = models.PositiveIntegerField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'skill']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.skill.name} ({self.get_proficiency_level_display()})"

class Project(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.ManyToManyField(Skill, blank=True)
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_ongoing = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} by {self.student.user.get_full_name()}"

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('award', 'Award'),
        ('certification', 'Certification'),
        ('competition', 'Competition'),
        ('scholarship', 'Scholarship'),
        ('recognition', 'Recognition'),
        ('publication', 'Publication'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    description = models.TextField()
    issuing_organization = models.CharField(max_length=200)
    date_achieved = models.DateField()
    certificate = models.FileField(upload_to='certificates/', blank=True)
    certificate_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['-date_achieved']
    
    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"

class Language(models.Model):
    PROFICIENCY_LEVELS = [
        ('elementary', 'Elementary'),
        ('limited_working', 'Limited Working'),
        ('professional_working', 'Professional Working'),
        ('full_professional', 'Full Professional'),
        ('native', 'Native/Bilingual'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(max_length=50)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    
    class Meta:
        unique_together = ['student', 'language']
    
    def __str__(self):
        return f"{self.language} ({self.get_proficiency_display()})"


class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('website', 'Website'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('medium', 'Medium'),
        ('devto', 'Dev.to'),
        ('stackoverflow', 'Stack Overflow'),
        ('kaggle', 'Kaggle'),
        ('behance', 'Behance'),
        ('dribbble', 'Dribbble'),
        ('telegram', 'Telegram'),
        ('custom', 'Custom'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=32, choices=PLATFORM_CHOICES)
    label = models.CharField(max_length=50, blank=True)
    url = models.URLField()
    is_public = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'platform')
        ordering = ['sort_order', 'platform']

    def __str__(self):
        lbl = self.label or self.get_platform_display()
        return f"{self.student.user.get_full_name() or self.student.user.email} — {lbl}"


class Preference(models.Model):
    """Catalog of student preferences/interests (e.g., internships, scholarships)."""
    key = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']

    def __str__(self):
        return f"{self.name} ({self.key})"


class StudentPreference(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='preferences')
    preference = models.ForeignKey(Preference, on_delete=models.CASCADE, related_name='student_preferences')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'preference')

    def __str__(self):
        return f"{self.student.user.get_full_name() or self.student.user.email} — {self.preference.name}"


# Academic Exams and Scores
class AcademicExam(models.Model):
    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Academic Exam'
        verbose_name_plural = 'Academic Exams'

    def __str__(self):
        return self.name


class AcademicExamSection(models.Model):
    exam = models.ForeignKey(AcademicExam, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)
    min_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=6, decimal_places=2)
    step = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        unique_together = ('exam', 'name')

    def __str__(self):
        return f"{self.exam.name} · {self.name}"


class StudentExamScore(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='exam_scores')
    exam = models.ForeignKey(AcademicExam, on_delete=models.CASCADE, related_name='student_scores')
    section = models.ForeignKey(AcademicExamSection, on_delete=models.CASCADE, related_name='student_scores')
    score = models.DecimalField(max_digits=7, decimal_places=2)
    taken_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'section')
        ordering = ['exam_id', 'section_id']

    def __str__(self):
        return f"{self.student.user.get_full_name() or self.student.user.email} · {self.exam.name} · {self.section.name}: {self.score}"
