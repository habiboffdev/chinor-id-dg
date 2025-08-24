from django.urls import path
from . import views

urlpatterns = [
    # Email Templates
    path('templates/', views.EmailTemplateListCreateView.as_view(), name='email-template-list-create'),
    path('templates/<int:pk>/', views.EmailTemplateDetailView.as_view(), name='email-template-detail'),
    
    # Messages
    path('messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('messages/<int:pk>/read/', views.mark_message_as_read, name='mark-message-read'),
    
    # Bulk Email
    path('send-bulk/', views.send_bulk_email, name='send-bulk-email'),
]
