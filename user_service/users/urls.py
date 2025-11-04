
from django.urls import path
from . import views

urlpatterns = [
    path('users/create/', views.create_user, name='create_user'),
    path('users/', views.list_users, name='list_users'),
    path('users/<uuid:user_id>/', views.get_user, name='get_user'),
    path('users/<uuid:user_id>/update/', views.update_user, name='update_user'),
    path('users/<uuid:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<uuid:user_id>/rollback/', views.rollback_user, name='rollback_user'),
]