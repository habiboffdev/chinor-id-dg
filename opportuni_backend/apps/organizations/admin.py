from django.contrib import admin
from .models import Organization, OrganizationMember


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization_type', 'user', 'is_verified', 'is_active', 'created_at')
    list_filter = ('organization_type', 'is_verified', 'is_active', 'country', 'created_at')
    search_fields = ('name', 'user__email', 'user__username', 'email', 'city')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'organization_type', 'description', 'logo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('country', 'city', 'address')
        }),
        ('Social Media', {
            'fields': ('linkedin_url', 'twitter_url', 'facebook_url')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'joined_at')
    list_filter = ('role', 'joined_at', 'organization__organization_type')
    search_fields = ('user__email', 'user__username', 'organization__name')
    ordering = ('-joined_at',)
