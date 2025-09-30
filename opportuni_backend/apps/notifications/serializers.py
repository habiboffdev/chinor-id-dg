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


# Action Response Serializers for OpenAPI Documentation
class MarkAllNotificationsReadResponseSerializer(serializers.Serializer):
    """Response serializer for marking all notifications as read"""
    message = serializers.CharField(help_text="Success message with count of notifications marked as read")


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total_count = serializers.IntegerField(help_text="Total number of notifications")
    unread_count = serializers.IntegerField(help_text="Number of unread notifications")
    read_count = serializers.IntegerField(help_text="Number of read notifications")
    recent_count = serializers.IntegerField(help_text="Number of notifications from last 7 days")
