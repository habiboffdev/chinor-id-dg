from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/details/', views.ProfileDetailView.as_view(), name='profile-details'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('telegram-auth/', views.telegram_auth, name='telegram-auth'),
    path('telegram-config/', views.telegram_config, name='telegram-config'),
]
