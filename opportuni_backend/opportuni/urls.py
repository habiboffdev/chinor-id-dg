"""
URL configuration for opportuni project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import IsAdminUser

# Restrict docs in production (staff-only); keep open in development
class StaffSpectacularAPIView(SpectacularAPIView):
    permission_classes = [IsAdminUser]


class StaffSpectacularSwaggerView(SpectacularSwaggerView):
    permission_classes = [IsAdminUser]


class StaffSpectacularRedocView(SpectacularRedocView):
    permission_classes = [IsAdminUser]

urlpatterns = [
    path('admin/', admin.site.urls),
]

# API Documentation
if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
else:
    urlpatterns += [
        path('api/schema/', StaffSpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', StaffSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', StaffSpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# API endpoints
urlpatterns += [
    path('api/auth/', include('apps.accounts.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/organizations/', include('apps.organizations.urls')),
    path('api/opportunities/', include('apps.opportunities.urls')),
    path('api/applications/', include('apps.applications.urls')),
    path('api/communications/', include('apps.communications.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
