from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Template views
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Authentication endpoints
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/register/', views.register_user, name='api-register'),
    path('api/upload/', views.upload_statement, name='api-upload'),
    path('api/advice/', views.investment_advice, name='api-advice'),
    path('api/chat/', views.ask_bot, name='api-chat'),
    path('api/profile/', views.get_profile, name='api-profile-get'),
    path('api/profile/save/', views.save_profile, name='api-profile-save'),
    path('api/logout/', views.logout_user, name='api-logout'),
    
    # New dashboard endpoints
    path('api/dashboard/', views.dashboard_data, name='api-dashboard'),
    path('api/expenses/', views.get_expenses, name='api-expenses'),
    path('api/recommendations/', views.recommendations, name='api-recommendations'),
]
