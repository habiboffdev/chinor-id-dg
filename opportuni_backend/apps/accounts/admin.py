from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'language', 'is_active', 'email_verified')
    list_filter = ('user_type', 'language', 'is_active', 'email_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'language', 'phone', 'avatar', 'email_verified')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'language', 'email', 'first_name', 'last_name')}),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'website')
    search_fields = ('user__email', 'user__username', 'location')
    list_filter = ('user__user_type',)
