from rest_framework import serializers
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
    
    def get_participants_names(self, obj):
        return [user.get_full_name() for user in obj.participants.all()]
    
    def get_last_message(self, obj):
        last_message = obj.participants.first()  # This would need proper implementation
        return None  # Placeholder
    
    def get_unread_count(self, obj):
        # This would need proper implementation based on user
        return 0
