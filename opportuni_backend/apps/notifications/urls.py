from django.urls import path
from . import views

urlpatterns = [
    # Notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/read/', views.mark_notification_as_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_as_read, name='mark-all-notifications-read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete-notification'),
    
    # Notification Settings
    path('settings/', views.NotificationSettingsView.as_view(), name='notification-settings'),
    
    # Statistics
    path('stats/', views.notification_stats, name='notification-stats'),
]
