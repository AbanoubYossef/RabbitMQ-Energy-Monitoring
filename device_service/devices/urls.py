from django.urls import path
from . import views

urlpatterns = [
    # User endpoints (for Saga)
    path('users/create/', views.create_user, name='create_user'),
    path('users/<uuid:user_id>/update/', views.update_user, name='update_user'),
    path('users/<uuid:user_id>/', views.delete_user, name='delete_user'),
    path('users/<uuid:user_id>/rollback/', views.rollback_user, name='rollback_user'),
    
    # Device endpoints
    path('devices/', views.list_devices, name='list_devices'),
    path('devices/create/', views.create_device, name='create_device'),
    path('devices/<uuid:device_id>/', views.get_device, name='get_device'),
    path('devices/<uuid:device_id>/update/', views.update_device, name='update_device'),
    path('devices/<uuid:device_id>/delete/', views.delete_device, name='delete_device'),
    
    # Device assignment endpoints
    path('devices/assign/', views.assign_device, name='assign_device'),
    path('devices/<uuid:device_id>/unassign/', views.unassign_device, name='unassign_device'),
    path('users/<uuid:user_id>/devices/', views.get_user_devices, name='get_user_devices'),
    path('mappings/', views.list_mappings, name='list_mappings'),
]