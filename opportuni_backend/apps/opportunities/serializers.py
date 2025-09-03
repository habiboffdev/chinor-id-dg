from rest_framework import serializers
from django.utils import timezone
from .models import Opportunity, OpportunityRequirement, OpportunityCategory, OpportunityQuestion
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


class OpportunitySerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    requirements = OpportunityRequirementSerializer(many=True, read_only=True)
    additional_questions = OpportunityQuestionSerializer(many=True, read_only=True)
    application_count = serializers.ReadOnlyField()
    can_apply = serializers.ReadOnlyField()
    is_deadline_passed = serializers.ReadOnlyField()
    days_until_deadline = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'organization', 'title', 'description', 'opportunity_type',
            'status', 'application_deadline', 'start_date', 'end_date',
            'required_skills', 'min_gpa', 'required_major', 'graduation_year_min',
            'graduation_year_max', 'age_min', 'age_max', 'location', 'is_remote', 'compensation',
            'benefits', 'cover_image', 'max_applications', 'featured', 'created_at',
            'updated_at', 'requirements', 'additional_questions', 'application_count', 
            'can_apply', 'is_deadline_passed', 'days_until_deadline'
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
        required=False
    )
    requirements = OpportunityRequirementSerializer(many=True, required=False)
    # Accept additional questions on create/update
    additional_questions = OpportunityQuestionSerializer(many=True, required=False)
    
    class Meta:
        model = Opportunity
        fields = [
            'title', 'description', 'opportunity_type', 'status',
            'application_deadline', 'start_date', 'end_date',
            'required_skills', 'min_gpa', 'required_major',
            'graduation_year_min', 'graduation_year_max', 'age_min', 'age_max', 'location',
            'is_remote', 'compensation', 'benefits', 'cover_image', 'max_applications',
            'featured', 'requirements', 'additional_questions'
        ]
    
    def create(self, validated_data):
        requirements_data = validated_data.pop('requirements', [])
        questions_data = validated_data.pop('additional_questions', [])

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

        return opportunity
    
    def update(self, instance, validated_data):
        requirements_data = validated_data.pop('requirements', [])
        questions_data = validated_data.pop('additional_questions', [])
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
    
    def get_opportunity_count(self, obj):
        return Opportunity.objects.filter(
            opportunity_type=obj.name.lower(),
            status='published'
        ).count()
