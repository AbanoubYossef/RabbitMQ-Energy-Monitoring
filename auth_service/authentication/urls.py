"""
authentication/urls.py
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    # Protected endpoints
    path('validate/', views.validate_token, name='validate_token'),
    path('users/', views.list_users, name='list_users'),
    path('users/<uuid:user_id>/', views.get_user_info, name='get_user_info'),
    path('users/<uuid:user_id>/update/', views.update_user, name='update_user'),
    path('users/<uuid:user_id>/delete/', views.delete_user, name='delete_user'),
]