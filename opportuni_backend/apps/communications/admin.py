from django.contrib import admin
from .models import EmailTemplate, Message, BulkEmail, EmailLog, MessageThread


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'template_type', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'organization__name', 'subject')
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'is_read', 'sent_at')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'body')
    ordering = ('-sent_at',)


@admin.register(BulkEmail)
class BulkEmailAdmin(admin.ModelAdmin):
    list_display = ('organization', 'subject', 'status', 'sent_count', 'failed_count', 'sent_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('organization__name', 'subject')
    ordering = ('-sent_at',)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender_organization', 'subject', 'delivered', 'opened', 'sent_at')
    list_filter = ('delivered', 'opened', 'clicked', 'sent_at')
    search_fields = ('recipient__email', 'subject')
    ordering = ('-sent_at',)


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('subject',)
    ordering = ('-updated_at',)
