from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.utils import timezone
from .models import Opportunity, OpportunityRequirement, OpportunityCategory, OpportunityQuestion, OpportunityProfileRequirement
from apps.students.models import Skill
from apps.organizations.serializers import OrganizationSerializer
from apps.students.serializers import SkillSerializer


class OpportunityRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityRequirement
        fields = ['id', 'requirement', 'is_mandatory', 'order']


class OpportunityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityQuestion
        fields = [
            'id', 'question', 'question_type', 'is_required', 'placeholder',
            'help_text', 'order', 'options', 'max_length', 'min_length'
        ]


class OpportunityProfileRequirementSerializer(serializers.ModelSerializer):
    section_display = serializers.CharField(source='get_section_display', read_only=True)
    requirement_level_display = serializers.CharField(source='get_requirement_level_display', read_only=True)
    
    class Meta:
        model = OpportunityProfileRequirement
        fields = ['id', 'section', 'section_display', 'requirement_level', 'requirement_level_display', 
                 'custom_message', 'minimum_items']


class OpportunitySerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    requirements = OpportunityRequirementSerializer(many=True, read_only=True)
    additional_questions = OpportunityQuestionSerializer(many=True, read_only=True)
    profile_requirements = OpportunityProfileRequirementSerializer(many=True, read_only=True)
    application_count = serializers.ReadOnlyField()
    can_apply = serializers.ReadOnlyField()
    is_deadline_passed = serializers.ReadOnlyField()
    days_until_deadline = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'organization', 'title', 'description', 'opportunity_type',
            'status', 'application_deadline', 'start_date', 'end_date', 'result_announcement_date',
            'required_skills', 'min_gpa', 'required_major', 'graduation_year_min',
            'graduation_year_max', 'age_min', 'age_max', 'location', 'is_remote', 'compensation',
            'benefits', 'application_instructions', 'cover_image', 'max_applications', 'featured', 'created_at',
            'updated_at', 'requirements', 'additional_questions', 'profile_requirements',
            'application_count', 'can_apply', 'is_deadline_passed', 'days_until_deadline'
        ]
    
    def get_days_until_deadline(self, obj):
        if obj.application_deadline:
            delta = obj.application_deadline - timezone.now()
            return delta.days if delta.days > 0 else 0
        return 0


class OpportunityCreateUpdateSerializer(serializers.ModelSerializer):
    # Make skills writable by ID
    required_skills = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        required=False,
        allow_empty=True
    )
    requirements = OpportunityRequirementSerializer(many=True, required=False)
    # Accept additional questions on create/update
    additional_questions = OpportunityQuestionSerializer(many=True, required=False)
    profile_requirements = OpportunityProfileRequirementSerializer(many=True, required=False)
    
    class Meta:
        model = Opportunity
        fields = [
            'title', 'description', 'opportunity_type', 'status',
            'application_deadline', 'start_date', 'end_date', 'result_announcement_date',
            'required_skills', 'min_gpa', 'required_major',
            'graduation_year_min', 'graduation_year_max', 'age_min', 'age_max', 'location',
            'is_remote', 'compensation', 'benefits', 'application_instructions', 'cover_image', 'max_applications',
            'featured', 'requirements', 'additional_questions', 'profile_requirements'
        ]
    
    def to_internal_value(self, data):
        # Handle FormData JSON strings for complex fields
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Parse JSON strings for complex fields when using FormData
        json_fields = ['requirements', 'additional_questions', 'profile_requirements']
        for field in json_fields:
            if field in mutable_data:
                value = mutable_data[field]
                if isinstance(value, str):
                    try:
                        import json
                        mutable_data[field] = json.loads(value)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        # If parsing fails, keep as is or set to empty list
                        mutable_data[field] = []
        
        return super().to_internal_value(mutable_data)
    
    def validate_required_skills(self, value):
        """Ensure required_skills contains only valid skill IDs"""
        if not value:
            return []
        
        # Filter out any non-integer values
        valid_ids = []
        for item in value:
            try:
                if hasattr(item, 'id'):
                    valid_ids.append(item)
                elif isinstance(item, int):
                    skill = Skill.objects.filter(id=item).first()
                    if skill:
                        valid_ids.append(skill)
                elif isinstance(item, str) and item.isdigit():
                    skill = Skill.objects.filter(id=int(item)).first()
                    if skill:
                        valid_ids.append(skill)
            except (ValueError, TypeError):
                continue
                
        return valid_ids
    
    def create(self, validated_data):
        requirements_data = validated_data.pop('requirements', [])
        questions_data = validated_data.pop('additional_questions', [])
        profile_requirements_data = validated_data.pop('profile_requirements', [])

        required_skills = validated_data.pop('required_skills', [])
        opportunity = Opportunity.objects.create(**validated_data)
        if required_skills:
            opportunity.required_skills.set(required_skills)

        for requirement_data in requirements_data:
            OpportunityRequirement.objects.create(
                opportunity=opportunity, **requirement_data
            )

        for q in questions_data:
            OpportunityQuestion.objects.create(opportunity=opportunity, **q)
        
        for pr in profile_requirements_data:
            OpportunityProfileRequirement.objects.create(opportunity=opportunity, **pr)

        return opportunity
    
    def update(self, instance, validated_data):
        requirements_data = validated_data.pop('requirements', [])
        questions_data = validated_data.pop('additional_questions', [])
        profile_requirements_data = validated_data.pop('profile_requirements', [])
        skills = validated_data.pop('required_skills', None)

        # Update opportunity fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update skills if provided
        if skills is not None:
            instance.required_skills.set(skills)

        # Replace requirements
        instance.requirements.all().delete()
        for requirement_data in requirements_data:
            OpportunityRequirement.objects.create(
                opportunity=instance, **requirement_data
            )

        # Replace additional questions
        instance.additional_questions.all().delete()
        for q in questions_data:
            OpportunityQuestion.objects.create(opportunity=instance, **q)
        
        # Replace profile requirements
        instance.profile_requirements.all().delete()
        for pr in profile_requirements_data:
            OpportunityProfileRequirement.objects.create(opportunity=instance, **pr)

        return instance


class OpportunityListSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_type = serializers.CharField(source='organization.organization_type', read_only=True)
    application_count = serializers.ReadOnlyField()
    days_until_deadline = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'title', 'organization_name', 'organization_type',
            'opportunity_type', 'status', 'location', 'is_remote',
            'application_deadline', 'featured', 'application_count',
            'days_until_deadline', 'created_at'
        ]
    
    def get_days_until_deadline(self, obj):
        if obj.application_deadline:
            delta = obj.application_deadline - timezone.now()
            return delta.days if delta.days > 0 else 0
        return 0


class OpportunityCategorySerializer(serializers.ModelSerializer):
    opportunity_count = serializers.SerializerMethodField()
    
    class Meta:
        model = OpportunityCategory
        fields = ['id', 'name', 'description', 'is_active', 'opportunity_count']
    
    @extend_schema_field(serializers.IntegerField)

    
    def get_opportunity_count(self, obj):
        return Opportunity.objects.filter(
            opportunity_type=obj.name.lower(),
            status='published'
        ).count()


# Action Response Serializers for OpenAPI Documentation
class OpportunityActionResponseSerializer(serializers.Serializer):
    """Response serializer for opportunity publish/close actions"""
    id = serializers.IntegerField(help_text="Opportunity ID")
    title = serializers.CharField(help_text="Opportunity title")
    status = serializers.CharField(help_text="Updated opportunity status")
    organization = serializers.IntegerField(help_text="Organization ID")
    deadline = serializers.DateTimeField(help_text="Application deadline")
    created_at = serializers.DateTimeField(help_text="Creation timestamp")
    updated_at = serializers.DateTimeField(help_text="Last update timestamp")


# Statistics and Debug Serializers for OpenAPI Documentation
class OpportunityStatsSerializer(serializers.Serializer):
    """Serializer for opportunity statistics"""
    total_opportunities = serializers.IntegerField(help_text="Total number of opportunities")
    published_opportunities = serializers.IntegerField(help_text="Number of published opportunities")
    draft_opportunities = serializers.IntegerField(help_text="Number of draft opportunities")
    closed_opportunities = serializers.IntegerField(help_text="Number of closed opportunities")
    total_applications = serializers.IntegerField(help_text="Total applications received")
    recent_applications = serializers.IntegerField(help_text="Applications in last 7 days")


class DebugOpportunitiesSerializer(serializers.Serializer):
    """Serializer for debug opportunities information"""
    user_type = serializers.CharField(help_text="Type of authenticated user")
    total_opportunities = serializers.IntegerField(help_text="Total opportunities in database")
    published_opportunities = serializers.IntegerField(help_text="Published opportunities count")
    future_deadlines = serializers.IntegerField(help_text="Opportunities with future deadlines")
    visible_opportunities = serializers.IntegerField(help_text="Opportunities visible to current user")
    user_organization_id = serializers.IntegerField(required=False, help_text="User's organization ID if applicable")
