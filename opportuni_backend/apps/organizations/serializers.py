from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember
from apps.opportunities.models import Opportunity
from apps.applications.models import Application

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    member_count = serializers.SerializerMethodField()
    opportunity_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'user_name', 'user_email', 'name', 'organization_type', 
            'description', 'logo', 'website', 'phone', 'email', 
            'country', 'city', 'address', 'linkedin_url', 'twitter_url', 
            'facebook_url', 'is_verified', 'is_active', 'created_at', 
            'updated_at', 'member_count', 'opportunity_count'
        ]
        read_only_fields = ('user', 'is_verified', 'created_at', 'updated_at')
    
    @extend_schema_field(serializers.IntegerField)

    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_opportunity_count(self, obj):
        try:
            return obj.opportunities.count()
        except Exception:
            return 0


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'name', 'organization_type', 'description', 'logo', 'website', 
            'phone', 'email', 'country', 'city', 'address', 'linkedin_url', 
            'twitter_url', 'facebook_url'
        ]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'user', 'user_name', 'user_email', 'organization', 
            'organization_name', 'role', 'joined_at'
        ]
        read_only_fields = ('organization', 'joined_at')


class OrganizationDashboardSerializer(serializers.ModelSerializer):
    total_opportunities = serializers.SerializerMethodField()
    total_applications = serializers.SerializerMethodField()
    pending_applications = serializers.SerializerMethodField()
    accepted_applications = serializers.SerializerMethodField()
    interviews_scheduled = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    recent_applications = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'name', 'organization_type', 'total_opportunities',
            'total_applications', 'pending_applications', 'accepted_applications',
            'interviews_scheduled', 'member_count', 'recent_applications'
        ]
    
    def get_total_opportunities(self, obj):
        return Opportunity.objects.filter(organization=obj).count()
    
    def get_total_applications(self, obj):
        return Application.objects.filter(opportunity__organization=obj).count()
    
    def get_pending_applications(self, obj):
        return Application.objects.filter(opportunity__organization=obj, status='pending').count()
    
    def get_accepted_applications(self, obj):
        return Application.objects.filter(opportunity__organization=obj, status='accepted').count()

    def get_interviews_scheduled(self, obj):
        return Application.objects.filter(opportunity__organization=obj, status='interview_scheduled').count()
    
    @extend_schema_field(serializers.IntegerField)

    
    def get_member_count(self, obj):
        return obj.members.count()
    
    @extend_schema_field(serializers.ListField)

    
    def get_recent_applications(self, obj):
        qs = Application.objects.filter(opportunity__organization=obj).select_related(
            'student__user', 'opportunity'
        ).order_by('-applied_at')[:6]
        out = []
        for app in qs:
            user = getattr(app.student, 'user', None)
            out.append({
                'id': app.id,
                'status': app.status,
                'applied_at': app.applied_at,
                'student_first_name': getattr(user, 'first_name', ''),
                'student_last_name': getattr(user, 'last_name', ''),
                'student_name': user.get_full_name() if user else '',
                'student_avatar': getattr(getattr(app.student, 'avatar', None), 'url', None) if hasattr(app.student, 'avatar') else None,
                'opportunity_id': app.opportunity_id,
                'opportunity_title': app.opportunity.title if app.opportunity else '',
            })
        return out


# File Upload Serializers for OpenAPI Documentation
class LogoUploadSerializer(serializers.Serializer):
    """Serializer for organization logo uploads"""
    logo = serializers.ImageField(
        help_text="Organization logo image file (JPEG, PNG, WebP). Max size: 5MB. Images will be resized appropriately."
    )
    
    def validate_logo(self, value):
        """Validate uploaded logo file"""
        # File size validation (5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size too large. Maximum size is 5MB.")
        
        # File type validation
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Invalid file type. Only JPEG, PNG, and WebP are allowed.")
        
        return value


class LogoUploadResponseSerializer(serializers.Serializer):
    """Response serializer for successful logo upload"""
    id = serializers.IntegerField(help_text="Organization ID")
    name = serializers.CharField(help_text="Organization name")
    logo = serializers.URLField(help_text="URL of the uploaded logo")
    description = serializers.CharField(help_text="Organization description")
    website = serializers.URLField(required=False, help_text="Organization website")


# Organization Management Serializers for OpenAPI Documentation
class InviteMemberSerializer(serializers.Serializer):
    """Serializer for inviting a member to organization"""
    email = serializers.EmailField(help_text="Email address of the user to invite")
    role = serializers.ChoiceField(
        choices=[('admin', 'Admin'), ('editor', 'Editor'), ('viewer', 'Viewer')],
        default='viewer',
        help_text="Role to assign to the invited member"
    )


class InviteMemberResponseSerializer(serializers.Serializer):
    """Response serializer for successful member invitation"""
    message = serializers.CharField(help_text="Success message")
    member = OrganizationMemberSerializer(help_text="Created member object")


class InviteStudentsSerializer(serializers.Serializer):
    """Serializer for inviting students to opportunities"""
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of student profile IDs to invite"
    )
    message = serializers.CharField(
        required=False,
        help_text="Optional message to include with the invitation"
    )


class InviteStudentsResponseSerializer(serializers.Serializer):
    """Response serializer for student invitation"""
    message = serializers.CharField(help_text="Success message")
    invited_count = serializers.IntegerField(help_text="Number of students invited")


class StudentStatsSerializer(serializers.Serializer):
    """Serializer for student statistics"""
    total_students = serializers.IntegerField(help_text="Total number of students")
    active_students = serializers.IntegerField(help_text="Number of active students")
    students_with_applications = serializers.IntegerField(help_text="Students who have applied")
    top_universities = serializers.ListField(
        child=serializers.DictField(),
        help_text="Top universities with student counts"
    )
    top_majors = serializers.ListField(
        child=serializers.DictField(),
        help_text="Top majors with student counts"
    )
