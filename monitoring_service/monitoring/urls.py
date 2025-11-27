from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeviceMeasurementViewSet,
    HourlyEnergyConsumptionViewSet,
    DeviceViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register(r'measurements', DeviceMeasurementViewSet, basename='measurement')
router.register(r'hourly', HourlyEnergyConsumptionViewSet, basename='hourly')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
