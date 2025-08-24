from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory, ApplicationAnswer


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0


class ApplicationNoteInline(admin.TabularInline):
    model = ApplicationNote
    extra = 0


class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ('changed_at',)


class ApplicationAnswerInline(admin.TabularInline):
    model = ApplicationAnswer
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('question', 'answer_text', 'answer_file', 'created_at')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'applied_at', 'updated_at', 'documents_count')
    list_filter = ('status', 'applied_at', 'opportunity__opportunity_type', 'opportunity__organization')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'opportunity__title', 'opportunity__organization__name')
    ordering = ('-applied_at',)
    inlines = [ApplicationAnswerInline, ApplicationDocumentInline, ApplicationNoteInline, ApplicationStatusHistoryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'opportunity', 'status')
        }),
        ('Application Content', {
            'fields': ('display_documents', 'additional_documents', 'reviewer_notes')
        }),
        ('Review Information', {
            'fields': ('interview_date', 'interview_notes')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at', 'reviewed_at')
        }),
    )
    
    readonly_fields = ('applied_at', 'updated_at', 'display_documents')
    
    def documents_count(self, obj):
        """Show count of additional documents"""
        if obj.additional_documents:
            return f"{len(obj.additional_documents)} files"
        return "No files"
    documents_count.short_description = "Documents"
    
    def display_documents(self, obj):
        """Display additional documents as clickable links"""
        if not obj.additional_documents:
            return "No additional documents uploaded"
        
        html = "<div style='margin-top: 10px;'>"
        html += "<strong>Additional Documents:</strong><br>"
        
        for i, doc_url in enumerate(obj.additional_documents):
            # Extract filename from URL
            filename = doc_url.split('/')[-1]
            # Create a clickable link
            html += f"<a href='{doc_url}' target='_blank' style='margin-right: 10px; display: inline-block; margin-bottom: 5px;'>"
            html += f"📄 {filename}</a><br>"
        
        html += "</div>"
        return format_html(html)
    display_documents.short_description = "Uploaded Documents"


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('application__student__user__first_name', 'application__student__user__last_name', 'application__opportunity__title')


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    list_display = ('application', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('application__student__user__first_name', 'application__student__user__last_name', 'note', 'author__username')


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = ('application__student__user__first_name', 'application__student__user__last_name', 'changed_by__username')
    readonly_fields = ('changed_at',)


@admin.register(ApplicationAnswer)
class ApplicationAnswerAdmin(admin.ModelAdmin):
    list_display = ('application', 'question', 'answer_text_preview', 'created_at')
    list_filter = ('question__question_type', 'created_at')
    search_fields = ('application__student__user__first_name', 'application__student__user__last_name', 'question__question', 'answer_text')
    
    def answer_text_preview(self, obj):
        if obj.answer_text:
            return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
        return '-'
    answer_text_preview.short_description = 'Answer Preview'
