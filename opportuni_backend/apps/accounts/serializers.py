from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from apps.students.models import StudentProfile
from apps.organizations.models import Organization, OrganizationMember

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    organization_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Organization.ORGANIZATION_TYPES],
        write_only=True,
        required=False,
    )
    organization_description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    organization_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    organization_country = serializers.CharField(write_only=True, required=False, allow_blank=True)
    organization_city = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'user_type',
            'password',
            'password_confirm',
            'organization_name',
            'organization_type',
            'organization_description',
            'organization_email',
            'organization_country',
            'organization_city',
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")

        user_type = attrs.get('user_type')
        if user_type == 'organization':
            required_fields = {
                'organization_name': 'Organization name is required for organization accounts.',
                'organization_type': 'Organization type is required for organization accounts.',
                'organization_country': 'Country is required for organization accounts.',
                'organization_city': 'City is required for organization accounts.',
            }
            errors = {}
            for field, message in required_fields.items():
                value = attrs.get(field)
                if not value:
                    errors[field] = [message]
            if errors:
                raise serializers.ValidationError(errors)
        return attrs
    
    def create(self, validated_data):
        password_confirm = validated_data.pop('password_confirm')
        org_payload = {
            'name': validated_data.pop('organization_name', '').strip(),
            'organization_type': validated_data.pop('organization_type', '').strip(),
            'description': validated_data.pop('organization_description', '').strip(),
            'email': validated_data.pop('organization_email', '').strip(),
            'country': validated_data.pop('organization_country', '').strip(),
            'city': validated_data.pop('organization_city', '').strip(),
        }

        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            Profile.objects.create(user=user)

            if user.user_type == 'student':
                StudentProfile.objects.get_or_create(user=user)

            if user.user_type == 'organization':
                organization_kwargs = {
                    'user': user,
                    'name': org_payload['name'] or user.get_full_name() or user.email,
                    'organization_type': org_payload['organization_type'],
                    'description': org_payload['description'] or 'Organization profile to be completed.',
                    'email': org_payload['email'] or user.email,
                    'country': org_payload['country'],
                    'city': org_payload['city'],
                }
                organization = Organization.objects.create(**organization_kwargs)
                OrganizationMember.objects.create(
                    organization=organization,
                    user=user,
                    role='admin'
                )

        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'user_type', 
                 'phone', 'avatar', 'email_verified', 'created_at', 'updated_at')
        read_only_fields = ('id', 'email_verified', 'created_at', 'updated_at')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


# Auth Action Serializers for OpenAPI Documentation
class LogoutResponseSerializer(serializers.Serializer):
    """Response serializer for logout"""
    message = serializers.CharField(help_text="Logout success message")


class TelegramAuthSerializer(serializers.Serializer):
    """Serializer for Telegram authentication data"""
    id = serializers.IntegerField(help_text="Telegram user ID")
    username = serializers.CharField(required=False, help_text="Telegram username")
    first_name = serializers.CharField(required=False, help_text="First name from Telegram")
    last_name = serializers.CharField(required=False, help_text="Last name from Telegram")
    auth_date = serializers.IntegerField(help_text="Authentication timestamp")
    hash = serializers.CharField(help_text="Authentication hash")


class TelegramAuthResponseSerializer(serializers.Serializer):
    """Response serializer for Telegram authentication"""
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user = serializers.DictField(help_text="User information")


class TelegramConfigSerializer(serializers.Serializer):
    """Serializer for Telegram bot configuration"""
    bot_username = serializers.CharField(required=False, help_text="Telegram bot username")
