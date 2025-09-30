from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.utils import timezone
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory, ApplicationAnswer
from apps.opportunities.serializers import OpportunityListSerializer
from apps.students.serializers import StudentProfileSerializer


class ApplicationAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    
    class Meta:
        model = ApplicationAnswer
        fields = ['id', 'question', 'question_text', 'question_type', 'answer_text', 'answer_file']


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = ['id', 'document', 'document_type', 'uploaded_at']


class ApplicationNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = ApplicationNote
        fields = ['id', 'author', 'author_name', 'note', 'is_internal', 'created_at']
        read_only_fields = ('author',)


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ApplicationStatusHistory
        fields = ['id', 'old_status', 'new_status', 'changed_by', 'changed_by_name', 'changed_at', 'reason']


class ApplicationSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    opportunity = OpportunityListSerializer(read_only=True)
    documents = ApplicationDocumentSerializer(many=True, read_only=True)
    notes = ApplicationNoteSerializer(many=True, read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    answers = ApplicationAnswerSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    opportunity_title = serializers.CharField(source='opportunity.title', read_only=True)
    organization_name = serializers.CharField(source='opportunity.organization.name', read_only=True)
    days_since_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'student', 'opportunity', 'status',
            'additional_documents', 'applied_at', 'updated_at', 'reviewed_at',
            'reviewer_notes', 'interview_date', 'interview_notes',
            'documents', 'notes', 'status_history', 'answers', 'student_name',
            'opportunity_title', 'organization_name', 'days_since_applied'
        ]
    
    @extend_schema_field(serializers.IntegerField)
    def get_days_since_applied(self, obj):
        delta = timezone.now() - obj.applied_at
        return delta.days


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['opportunity']
    
    def validate_opportunity(self, value):
        # Check if opportunity can accept applications
        if not value.can_apply:
            raise serializers.ValidationError("This opportunity is not accepting applications.")
        
        # Check if student already applied
        request = self.context.get('request')
        if request and hasattr(request.user, 'studentprofile'):
            if Application.objects.filter(
                student=request.user.studentprofile,
                opportunity=value
            ).exists():
                raise serializers.ValidationError("You have already applied to this opportunity.")
        
        return value


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status', 'reviewer_notes', 'interview_date', 'interview_notes', 'reviewed_at']


class ApplicationListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_email = serializers.CharField(source='student.user.email', read_only=True)
    student_university = serializers.CharField(source='student.university', read_only=True)
    opportunity_title = serializers.CharField(source='opportunity.title', read_only=True)
    organization_name = serializers.CharField(source='opportunity.organization.name', read_only=True)
    days_since_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'student', 'opportunity', 'status', 'applied_at',
            'updated_at', 'student_name', 'student_email', 'student_university',
            'opportunity_title', 'organization_name', 'days_since_applied'
        ]
    
    def get_days_since_applied(self, obj):
        delta = timezone.now() - obj.applied_at
        return delta.days


class BulkStatusUpdateSerializer(serializers.Serializer):
    application_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    status = serializers.ChoiceField(choices=Application.STATUS_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True)


# File Upload Serializers for OpenAPI Documentation
class ApplicationDocumentUploadSerializer(serializers.Serializer):
    """Serializer for application document uploads"""
    file = serializers.FileField(
        help_text="Document file (PDF, DOC, DOCX, TXT, JPG, PNG). Max size: 10MB."
    )
    
    def validate_file(self, value):
        """Validate uploaded document file"""
        # File size validation (10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size too large. Maximum size is 10MB.")
        
        # File type validation
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/jpg',
            'image/png'
        ]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Invalid file type. Allowed: PDF, DOC, DOCX, TXT, JPG, PNG.")
        
        return value


class ApplicationDocumentUploadResponseSerializer(serializers.Serializer):
    """Response serializer for successful document upload"""
    file_url = serializers.URLField(help_text="URL of the uploaded document")
    filename = serializers.CharField(help_text="Original filename")
    size = serializers.IntegerField(help_text="File size in bytes")
    content_type = serializers.CharField(help_text="MIME type of the uploaded file")
