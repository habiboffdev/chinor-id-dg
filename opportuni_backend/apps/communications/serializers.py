from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import EmailTemplate, Message, BulkEmail, MessageThread


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'subject', 'body', 
            'variables', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'recipient', 'recipient_name',
            'subject', 'body', 'is_read', 'sent_at', 'read_at',
            'application', 'opportunity'
        ]
        read_only_fields = ('sender', 'sent_at', 'read_at')


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body', 'application', 'opportunity']


class BulkEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkEmail
        fields = [
            'id', 'template', 'subject', 'body', 'recipients', 
            'sent_at', 'sent_count', 'failed_count', 'status'
        ]
        read_only_fields = ('sent_at', 'sent_count', 'failed_count', 'status')


class MessageThreadSerializer(serializers.ModelSerializer):
    participants_names = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageThread
        fields = [
            'id', 'subject', 'participants', 'participants_names',
            'created_at', 'updated_at', 'application', 'opportunity',
            'last_message', 'unread_count'
        ]
    
    @extend_schema_field(serializers.CharField)

    
    def get_participants_names(self, obj):
        return [user.get_full_name() for user in obj.participants.all()]
    
    @extend_schema_field(serializers.DictField)

    
    def get_last_message(self, obj):
        last_message = obj.participants.first()  # This would need proper implementation
        return None  # Placeholder
    
    @extend_schema_field(serializers.IntegerField)

    
    def get_unread_count(self, obj):
        # This would need proper implementation based on user
        return 0


# Action Response Serializers for OpenAPI Documentation  
# MessageSerializer already exists and can be reused for mark_message_as_read response

class BulkEmailRequestSerializer(serializers.Serializer):
    """Serializer for bulk email request"""
    template_id = serializers.IntegerField(required=False, help_text="Optional email template ID")
    subject = serializers.CharField(help_text="Email subject")
    body = serializers.CharField(help_text="Email body content")
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of recipient user IDs"
    )


class BulkEmailResponseSerializer(serializers.Serializer):
    """Response serializer for bulk email"""
    message = serializers.CharField(help_text="Success message")
    sent_count = serializers.IntegerField(help_text="Number of emails sent")
    bulk_email_id = serializers.IntegerField(help_text="Created bulk email record ID")
