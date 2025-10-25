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
    answers = serializers.JSONField(required=False, allow_null=True, help_text="Answers to opportunity questions as {question_id: answer_text}")
    
    class Meta:
        model = Application
        fields = ['opportunity', 'answers', 'additional_documents']
    
    def to_representation(self, instance):
        """Return properly serialized application data using ApplicationSerializer"""
        return ApplicationSerializer(instance, context=self.context).data
    
    def validate_opportunity(self, value):
        # Check if opportunity can accept applications
        if not value.can_apply:
            raise serializers.ValidationError("Ushbu imkoniyat hozirda arizalar qabul qilmayapti.")
        
        # Check if student already applied
        request = self.context.get('request')
        if request and hasattr(request.user, 'studentprofile'):
            if Application.objects.filter(
                student=request.user.studentprofile,
                opportunity=value
            ).exists():
                raise serializers.ValidationError("Siz bu imkoniyatga allaqachon ariza topshirgansiz.")
        
        return value
    
    def validate(self, attrs):
        """
        🔴 CRITICAL: Validate all required questions are answered with non-empty values
        Also validates min_length and max_length constraints for all answers
        """
        opportunity = attrs.get('opportunity')
        answers = attrs.get('answers')
        
        # Handle null answers - convert to empty dict
        if answers is None:
            answers = {}
            attrs['answers'] = {}
        
        if not opportunity:
            raise serializers.ValidationError({"opportunity": "Imkoniyat tanlanishi shart."})
        
        # 🔴 CRITICAL: Validate profile requirements BEFORE question validation
        # This must be in validate() not create() so DRF returns 400 not 500
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'student_profile'):
            student_profile = request.user.student_profile
            self.validate_profile_requirements(opportunity, student_profile)
        
        # Get all questions for this opportunity (required and optional)
        all_questions = opportunity.additional_questions.all()
        required_questions = all_questions.filter(is_required=True)
        
        # Validation error lists
        missing_questions = []
        empty_answers = []
        length_errors = []
        
        # Step 1: Validate required questions are answered and not empty
        if required_questions.exists():
            for question in required_questions:
                question_key = str(question.id)
                
                # Check if answer exists in the answers dict
                if question_key not in answers:
                    missing_questions.append(question.question)
                    continue
                
                # Check if answer is not empty (strip whitespace)
                answer_value = answers.get(question_key)
                if answer_value is None or str(answer_value).strip() == '':
                    empty_answers.append(question.question)
        
        # Step 2: Validate min_length and max_length for ALL provided answers
        for question in all_questions:
            question_key = str(question.id)
            
            # Skip if no answer provided for optional questions
            if question_key not in answers:
                continue
            
            answer_value = answers.get(question_key)
            
            # Skip empty answers (already caught above if required)
            if answer_value is None or str(answer_value).strip() == '':
                continue
            
            answer_text = str(answer_value).strip()
            
            # Count words (split by whitespace and filter empty strings)
            words = [word for word in answer_text.split() if word]
            word_count = len(words)
            
            # Validate min_length (WORD count)
            if question.min_length and word_count < question.min_length:
                length_errors.append(
                    f"{question.question}: kamida {question.min_length} ta so'z kerak "
                    f"({word_count} ta so'z kiritilgan)"
                )
            
            # Validate max_length (WORD count)
            if question.max_length and word_count > question.max_length:
                length_errors.append(
                    f"{question.question}: maksimum {question.max_length} ta so'z ruxsat etilgan "
                    f"({word_count} ta so'z kiritilgan)"
                )
        
        # Raise validation errors with clear messages
        error_messages = []
        
        if missing_questions:
            error_messages.append(f"Javob berilmagan majburiy savollar: {', '.join(missing_questions)}")
        
        if empty_answers:
            error_messages.append(f"Bo'sh qoldirilgan majburiy savollar: {', '.join(empty_answers)}")
        
        if length_errors:
            error_messages.append("Javob uzunligi talablariga mos kelmaydi: " + " | ".join(length_errors))
        
        if error_messages:
            raise serializers.ValidationError({
                "answers": " | ".join(error_messages)
            })
        
        return attrs
    
    def validate_profile_requirements(self, opportunity, student_profile):
        """🔴 CRITICAL: Validate student profile meets opportunity requirements"""
        required_profile_reqs = opportunity.profile_requirements.filter(
            requirement_level='required'
        )
        
        if not required_profile_reqs.exists():
            return  # No profile requirements to validate
        
        missing_requirements = []
        
        for req in required_profile_reqs:
            section = req.section
            minimum = req.minimum_items or 1
            
            # Check each section
            if section == 'education':
                count = student_profile.education.count()
            elif section == 'experience':
                count = student_profile.experiences.count()
            elif section == 'skills':
                count = student_profile.skills.count()
            elif section == 'projects':
                count = student_profile.projects.count()
            elif section == 'languages':
                count = student_profile.languages.count()
            elif section == 'certifications':
                count = student_profile.certifications.count()
            elif section == 'awards':
                count = student_profile.awards.count()
            elif section == 'resume':
                count = 1 if student_profile.resume else 0
            elif section == 'linkedin':
                count = 1 if student_profile.linkedin_url else 0
            elif section == 'github':
                count = 1 if student_profile.github_url else 0
            elif section == 'website':
                count = 1 if student_profile.website_url else 0
            elif section == 'personal_statement':
                count = 1 if student_profile.bio else 0
            elif section == 'portfolio':
                count = 1 if student_profile.portfolio_url else 0
            else:
                continue
            
            if count < minimum:
                section_name = dict(req.PROFILE_SECTIONS).get(section, section)
                if req.custom_message:
                    missing_requirements.append(req.custom_message)
                else:
                    missing_requirements.append(
                        f"{section_name}: kamida {minimum} ta kerak, {count} ta mavjud"
                    )
        
        if missing_requirements:
            raise serializers.ValidationError({
                "profile": " | ".join(missing_requirements)
            })
    
    def create(self, validated_data):
        """Create application and save answers"""
        from django.db import transaction
        
        answers_data = validated_data.pop('answers', {})
        
        # Profile requirements already validated in validate() method
        # Use atomic transaction to ensure both application and answers are created together
        with transaction.atomic():
            # Create application (student will be added in perform_create)
            application = Application.objects.create(**validated_data)
            
            # Create ApplicationAnswer records
            if answers_data:
                from apps.opportunities.models import OpportunityQuestion
                for question_id_str, answer_value in answers_data.items():
                    try:
                        question_id = int(question_id_str)
                        question = OpportunityQuestion.objects.get(
                            id=question_id,
                            opportunity=application.opportunity
                        )
                        
                        # Only create if answer is not empty
                        answer_text = str(answer_value).strip()
                        if answer_text:
                            ApplicationAnswer.objects.create(
                                application=application,
                                question=question,
                                answer_text=answer_text
                            )
                    except (ValueError, TypeError, OpportunityQuestion.DoesNotExist):
                        # Log this but don't fail - could be deleted question or invalid ID
                        continue
        
        # Refresh from database to get related fields
        application.refresh_from_db()
        return application


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
