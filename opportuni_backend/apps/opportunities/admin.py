from django.contrib import admin
from .models import Opportunity, OpportunityRequirement, OpportunityCategory, OpportunityQuestion


class OpportunityRequirementInline(admin.TabularInline):
    model = OpportunityRequirement
    extra = 1


class OpportunityQuestionInline(admin.TabularInline):
    model = OpportunityQuestion
    extra = 1
    fields = ('question', 'question_type', 'is_required', 'order', 'min_length', 'max_length')
    ordering = ('order',)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'opportunity_type', 'status', 'application_deadline', 'featured', 'created_at')
    list_filter = ('opportunity_type', 'status', 'is_remote', 'featured', 'created_at', 'organization__organization_type')
    search_fields = ('title', 'description', 'organization__name', 'location')
    ordering = ('-created_at',)
    inlines = [OpportunityQuestionInline, OpportunityRequirementInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'title', 'description', 'opportunity_type', 'status', 'cover_image')
        }),
        ('Dates', {
            'fields': ('application_deadline', 'start_date', 'end_date')
        }),
        ('Requirements', {
            'fields': ('required_skills', 'min_gpa', 'required_major', 'graduation_year_min', 'graduation_year_max')
        }),
        ('Location & Details', {
            'fields': ('location', 'is_remote', 'compensation', 'benefits')
        }),
        ('Settings', {
            'fields': ('max_applications', 'featured')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('required_skills',)


@admin.register(OpportunityCategory)
class OpportunityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(OpportunityRequirement)
class OpportunityRequirementAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'requirement', 'is_mandatory', 'order')
    list_filter = ('is_mandatory', 'opportunity__opportunity_type')
    search_fields = ('opportunity__title', 'requirement')
    ordering = ('opportunity', 'order')


@admin.register(OpportunityQuestion)
class OpportunityQuestionAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'question_preview', 'question_type', 'is_required', 'order')
    list_filter = ('question_type', 'is_required', 'opportunity__opportunity_type')
    search_fields = ('opportunity__title', 'question')
    ordering = ('opportunity', 'order')
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'
