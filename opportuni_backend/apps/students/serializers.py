from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    StudentProfile, Education, Experience, Skill, StudentSkill,
    Project, Achievement, Language, SocialLink,
    AcademicExam, AcademicExamSection, StudentExamScore,
)

User = get_user_model()

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class StudentSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = StudentSkill
        fields = ['id', 'skill', 'skill_id', 'proficiency_level', 'years_experience', 'verified']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['student']
        extra_kwargs = {
            'end_date': { 'required': False, 'allow_null': True },
            'description': { 'required': False, 'allow_blank': True },
            'gpa': { 'required': False, 'allow_null': True },
        }

    def validate(self, attrs):
        # Normalize empty string to None for end_date
        end_date = attrs.get('end_date', None)
        if end_date == '':
            attrs['end_date'] = None
        is_current = attrs.get('is_current', False)
        if is_current:
            attrs['end_date'] = None
        return super().validate(attrs)

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'
        read_only_fields = ['student']
        extra_kwargs = {
            'end_date': { 'required': False, 'allow_null': True },
            'location': { 'required': False, 'allow_blank': True },
        }

    def validate(self, attrs):
        end_date = attrs.get('end_date', None)
        if end_date == '':
            attrs['end_date'] = None
        if attrs.get('is_current', False):
            attrs['end_date'] = None
        return super().validate(attrs)

class ProjectSerializer(serializers.ModelSerializer):
    technologies = SkillSerializer(many=True, read_only=True)
    technology_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['student']
        extra_kwargs = {
            'end_date': { 'required': False, 'allow_null': True },
            'project_url': { 'required': False, 'allow_blank': True },
            'github_url': { 'required': False, 'allow_blank': True },
        }

    def validate(self, attrs):
        end_date = attrs.get('end_date', None)
        if end_date == '':
            attrs['end_date'] = None
        if attrs.get('is_ongoing', False):
            attrs['end_date'] = None
        return super().validate(attrs)
    
    def create(self, validated_data):
        technology_ids = validated_data.pop('technology_ids', [])
        project = Project.objects.create(**validated_data)
        if technology_ids:
            project.technologies.set(technology_ids)
        return project
    
    def update(self, instance, validated_data):
        technology_ids = validated_data.pop('technology_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if technology_ids is not None:
            instance.technologies.set(technology_ids)
        
        return instance

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'
        read_only_fields = ['student']

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
        read_only_fields = ['student']


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'
        read_only_fields = ['student']


class AcademicExamSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicExamSection
        fields = ['id', 'name', 'min_score', 'max_score', 'step', 'sort_order']


class AcademicExamSerializer(serializers.ModelSerializer):
    sections = AcademicExamSectionSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicExam
        fields = ['id', 'slug', 'name', 'description', 'sections']


class StudentExamScoreSerializer(serializers.ModelSerializer):
    exam = AcademicExamSerializer(read_only=True)
    section = AcademicExamSectionSerializer(read_only=True)
    exam_id = serializers.IntegerField(write_only=True)
    section_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = StudentExamScore
        fields = ['id', 'exam', 'section', 'exam_id', 'section_id', 'score', 'taken_date', 'notes']
        read_only_fields = []

    def validate(self, attrs):
        exam_id = attrs.get('exam_id')
        section_id = attrs.get('section_id')
        score = attrs.get('score')
        # Ensure section belongs to exam and score within bounds
        try:
            section = AcademicExamSection.objects.get(id=section_id, exam_id=exam_id)
        except AcademicExamSection.DoesNotExist:
            raise serializers.ValidationError('Invalid exam/section combination')
        if score is None or not (section.min_score <= score <= section.max_score):
            raise serializers.ValidationError(f'Score must be between {section.min_score} and {section.max_score}')
        # Check step with decimals safely
        try:
            from decimal import Decimal, getcontext
            getcontext().prec = 10
            step = Decimal(section.step)
            base = Decimal(section.min_score)
            s = Decimal(score)
            if step > 0:
                remainder = (s - base) % step
                if remainder != 0:
                    # Allow small floating rounding tolerance
                    if remainder.copy_abs() > Decimal('0.0001') and (step - remainder).copy_abs() > Decimal('0.0001'):
                        raise serializers.ValidationError(f'Score must be in increments of {section.step}')
        except Exception:
            pass
        return attrs

class StudentProfileSerializer(serializers.ModelSerializer):
    # User fields
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    
    # Related fields
    user = serializers.StringRelatedField(read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    skills = StudentSkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    achievements = AchievementSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['user', 'student_id', 'created_at', 'updated_at']

class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [
            'phone', 'date_of_birth', 'location', 'bio', 'university',
            'major', 'graduation_year', 'gpa', 'portfolio_url', 'about_me',
            'phone_visible', 'email_visible'
        ]
        extra_kwargs = {
            'phone': {'required': False, 'allow_blank': True},
            'date_of_birth': {'required': False, 'allow_null': True},
            'location': {'required': False, 'allow_blank': True},
            'bio': {'required': False, 'allow_blank': True},
            'university': {'required': False, 'allow_blank': True},
            'major': {'required': False, 'allow_blank': True},
            'graduation_year': {'required': False, 'allow_null': True},
            'gpa': {'required': False, 'allow_null': True},
            'portfolio_url': {'required': False, 'allow_blank': True},
            'about_me': {'required': False, 'allow_blank': True},
            'phone_visible': {'required': False},
            'email_visible': {'required': False},
        }
    
    def update(self, instance, validated_data):
        # Get the original request data to access user fields
        request_data = self.context['request'].data
        
        # Extract user fields from request data
        user_fields = ['first_name', 'last_name', 'email']
        user_data = {}
        for field in user_fields:
            if field in request_data:
                user_data[field] = request_data[field]
        
        # Update user fields
        if user_data:
            user = instance.user
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()
        
        # Update profile fields (these are in validated_data)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        
        return instance

class StudentDashboardSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    total_applications = serializers.SerializerMethodField()
    pending_applications = serializers.SerializerMethodField()
    accepted_applications = serializers.SerializerMethodField()
    rejected_applications = serializers.SerializerMethodField()
    recent_applications = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'user_name', 'user_email', 'university', 'major', 'graduation_year',
            'total_applications', 'pending_applications', 'accepted_applications', 
            'rejected_applications', 'recent_applications', 'profile_completion'
        ]
    
    def get_total_applications(self, obj):
        try:
            from apps.applications.models import Application
            return Application.objects.filter(student=obj).count()
        except:
            return 0
    
    def get_pending_applications(self, obj):
        try:
            from apps.applications.models import Application
            return Application.objects.filter(student=obj, status='pending').count()
        except:
            return 0
    
    def get_accepted_applications(self, obj):
        try:
            from apps.applications.models import Application
            return Application.objects.filter(student=obj, status='accepted').count()
        except:
            return 0
    
    def get_rejected_applications(self, obj):
        try:
            from apps.applications.models import Application
            return Application.objects.filter(student=obj, status='rejected').count()
        except:
            return 0
    
    def get_recent_applications(self, obj):
        try:
            from apps.applications.models import Application
            recent_apps = Application.objects.filter(student=obj).order_by('-applied_at')[:5]
            return [{
                'id': app.id,
                'opportunity_title': app.opportunity.title,
                'organization_name': app.opportunity.organization.name,
                'status': app.status,
                'applied_at': app.applied_at.isoformat()
            } for app in recent_apps]
        except:
            return []
    
    def get_profile_completion(self, obj):
        # Calculate profile completion percentage
        fields_to_check = [
            obj.university, obj.major, obj.graduation_year, obj.about_me
        ]
        completed_fields = sum(1 for field in fields_to_check if field)
        
        # Check for related objects
        if obj.education.exists():
            completed_fields += 1
        if obj.experiences.exists():
            completed_fields += 1
        if obj.skills.exists():
            completed_fields += 1
        
        total_fields = len(fields_to_check) + 3  # +3 for education, experience, skills
        completion_percentage = (completed_fields / total_fields) * 100
        
        return {
            'percentage': round(completion_percentage, 1),
            'completed_fields': completed_fields,
            'total_fields': total_fields
        }
