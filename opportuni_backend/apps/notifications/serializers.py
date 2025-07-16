from rest_framework import serializers
from .models import Notification, NotificationSettings


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'data',
            'is_read', 'created_at', 'read_at'
        ]
        read_only_fields = ('created_at', 'read_at')


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = [
            'email_notifications', 'push_notifications', 'application_updates',
            'new_opportunities', 'deadline_reminders', 'messages', 'system_announcements'
        ]
