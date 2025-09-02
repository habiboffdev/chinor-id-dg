from django.urls import path
from . import views

urlpatterns = [
    # Application CRUD
    path('', views.ApplicationListCreateView.as_view(), name='application-list-create'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    # Organization-scoped listing (alias for clarity)
    path('org/', views.OrganizationApplicationListView.as_view(), name='organization-application-list'),
    
    # Application Documents
    path('<int:application_id>/documents/', views.ApplicationDocumentListCreateView.as_view(), name='application-document-list-create'),
    
    # Application Notes
    path('<int:application_id>/notes/', views.ApplicationNoteListCreateView.as_view(), name='application-note-list-create'),
    
    # Actions
    path('<int:pk>/withdraw/', views.withdraw_application, name='withdraw-application'),
    path('bulk-update/', views.bulk_update_status, name='bulk-update-status'),
    path('upload-document/', views.upload_application_document, name='upload-application-document'),
    
    # Statistics
    path('stats/', views.application_stats, name='application-stats'),
]
