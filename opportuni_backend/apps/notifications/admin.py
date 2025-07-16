from django.contrib import admin
from .models import Notification, NotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'read_at')


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'push_notifications', 'application_updates')
    list_filter = ('email_notifications', 'push_notifications', 'application_updates')
    search_fields = ('user__username', 'user__email')
