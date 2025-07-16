from django.urls import path
from . import views

urlpatterns = [
    # Opportunity CRUD
    path('', views.OpportunityListCreateView.as_view(), name='opportunity-list-create'),
    path('<int:pk>/', views.OpportunityDetailView.as_view(), name='opportunity-detail'),
    
    # Search and filtering
    path('search/', views.OpportunitySearchView.as_view(), name='opportunity-search'),
    path('featured/', views.FeaturedOpportunitiesView.as_view(), name='featured-opportunities'),
    
    # Categories
    path('categories/', views.OpportunityCategoryListView.as_view(), name='opportunity-categories'),
    
    # Actions
    path('<int:pk>/publish/', views.publish_opportunity, name='publish-opportunity'),
    path('<int:pk>/close/', views.close_opportunity, name='close-opportunity'),
    
    # Statistics
    path('stats/', views.opportunity_stats, name='opportunity-stats'),
    
    # Debug endpoint
    path('debug/', views.debug_opportunities, name='debug-opportunities'),
]
