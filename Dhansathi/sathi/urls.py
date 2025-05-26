from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('logout/', views.logout_user),
    path('profile/', views.save_profile),
    path('upload/', views.upload_statement),
    path('advice/', views.investment_advice),
    path('chat/', views.ask_bot),
    path('register/', views.register_user), 
]
