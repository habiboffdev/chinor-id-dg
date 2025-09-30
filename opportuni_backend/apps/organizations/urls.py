from django.urls import path
from . import views

urlpatterns = [
    # Organization Profile
    path('profile/', views.OrganizationProfileView.as_view(), name='organization-profile'),
    path('dashboard/', views.OrganizationDashboardView.as_view(), name='organization-dashboard'),
    
    # Organization Members
    path('members/', views.OrganizationMemberListCreateView.as_view(), name='organization-member-list-create'),
    path('members/<int:pk>/', views.OrganizationMemberDetailView.as_view(), name='organization-member-detail'),
    
    # Organization Search and List
    path('', views.OrganizationListView.as_view(), name='organization-list'),
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='organization-detail'),
    
    # Students Management
    path('students/stats/', views.get_student_stats, name='organization-student-stats'),
    path('students/', views.get_students, name='organization-students'),
    path('students/invite/', views.invite_students, name='organization-invite-students'),
    
    # File Upload and Actions
    path('upload-logo/', views.upload_logo, name='upload-logo'),
    path('invite-member/', views.invite_member, name='invite-member'),
]
