from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember

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
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_opportunity_count(self, obj):
        # This will be implemented when we create the Opportunities app
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
    member_count = serializers.SerializerMethodField()
    recent_applications = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'name', 'organization_type', 'total_opportunities', 
            'total_applications', 'pending_applications', 
            'accepted_applications', 'member_count', 'recent_applications'
        ]
    
    def get_total_opportunities(self, obj):
        # This will be implemented when we create the Opportunities app
        return 0
    
    def get_total_applications(self, obj):
        # This will be implemented when we create the Applications app
        return 0
    
    def get_pending_applications(self, obj):
        # This will be implemented when we create the Applications app
        return 0
    
    def get_accepted_applications(self, obj):
        # This will be implemented when we create the Applications app
        return 0
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_recent_applications(self, obj):
        # This will be implemented when we create the Applications app
        return []
