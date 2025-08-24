from django.contrib import admin
from .models import (
    StudentProfile,
    Education,
    Experience,
    Skill,
    StudentSkill,
    Project,
    Achievement,
    Language,
)


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    fields = (
        'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'gpa'
    )
    ordering = ('-start_date',)


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0
    fields = (
        'title', 'company', 'experience_type', 'start_date', 'end_date', 'is_current', 'location'
    )
    ordering = ('-start_date',)


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    fields = (
        'title', 'project_url', 'github_url', 'start_date', 'end_date', 'is_ongoing', 'featured'
    )
    filter_horizontal = ('technologies',)
    ordering = ('-start_date',)


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 0
    fields = (
        'title', 'achievement_type', 'issuing_organization', 'date_achieved', 'certificate', 'certificate_url'
    )
    ordering = ('-date_achieved',)


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0
    fields = ('language', 'proficiency')


class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 0
    fields = ('skill', 'proficiency_level', 'years_experience', 'verified')
    autocomplete_fields = ('skill',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'student_id', 'university', 'major', 'graduation_year', 'gpa', 'profile_completed', 'created_at'
    )
    list_filter = (
        'profile_completed', 'graduation_year', 'university', 'major', 'created_at', 'updated_at'
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name', 'student_id', 'university', 'major'
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {'fields': ('user', 'student_id')}),
        ('Personal Information', {
            'fields': ('phone', 'date_of_birth', 'location', 'bio')
        }),
        ('Academic Information', {
            'fields': ('university', 'major', 'graduation_year', 'gpa')
        }),
        ('Files and URLs', {
            'fields': ('resume', 'portfolio_url', 'about_me')
        }),
        ('Contact Preferences', {
            'fields': ('phone_visible', 'email_visible')
        }),
        ('Status', {'fields': ('profile_completed',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    inlines = [
        EducationInline,
        ExperienceInline,
        ProjectInline,
        AchievementInline,
        LanguageInline,
        StudentSkillInline,
    ]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('student', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'gpa')
    list_filter = ('degree', 'is_current', 'start_date', 'end_date')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'institution', 'field_of_study')
    ordering = ('-start_date',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'company', 'experience_type', 'start_date', 'end_date', 'is_current', 'location')
    list_filter = ('experience_type', 'is_current', 'start_date', 'end_date')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'title', 'company')
    ordering = ('-start_date',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('student', 'skill', 'proficiency_level', 'years_experience', 'verified')
    list_filter = ('proficiency_level', 'verified')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'skill__name')
    autocomplete_fields = ('student', 'skill')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'start_date', 'end_date', 'is_ongoing', 'featured')
    list_filter = ('is_ongoing', 'featured', 'start_date', 'end_date')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'title')
    filter_horizontal = ('technologies',)
    ordering = ('-start_date',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'achievement_type', 'issuing_organization', 'date_achieved')
    list_filter = ('achievement_type', 'date_achieved')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'title', 'issuing_organization')
    ordering = ('-date_achieved',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('student', 'language', 'proficiency')
    list_filter = ('proficiency',)
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'language')
