from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import DeviceMeasurement, HourlyEnergyConsumption, Device, User, UserDeviceMapping
from .serializers import (
    DeviceMeasurementSerializer,
    HourlyEnergyConsumptionSerializer,
    DeviceSerializer,
    UserSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


def get_user_devices(user):
    """Get device IDs accessible by the user based on their role"""
    if user.role == 'admin':
        # Admin can see all devices
        return Device.objects.all().values_list('id', flat=True)
    else:
        # Client can only see their assigned devices
        return UserDeviceMapping.objects.filter(user_id=user.id).values_list('device_id', flat=True)


class DeviceMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing device measurements
    """
    queryset = DeviceMeasurement.objects.all()
    serializer_class = DeviceMeasurementSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('device_id', OpenApiTypes.UUID, description='Filter by device ID'),
            OpenApiParameter('start_date', OpenApiTypes.DATETIME, description='Start date'),
            OpenApiParameter('end_date', OpenApiTypes.DATETIME, description='End date'),
        ]
    )
    def list(self, request):
        """List measurements - admin sees all, client sees only their devices"""
        # Get accessible device IDs based on user role
        accessible_device_ids = get_user_devices(request.user)
        
        # Filter queryset to only accessible devices
        queryset = self.get_queryset().filter(device_id__in=accessible_device_ids)
        
        device_id = request.query_params.get('device_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if device_id:
            # Verify user has access to this specific device
            if device_id not in [str(did) for did in accessible_device_ids]:
                return Response(
                    {'error': 'You do not have access to this device'},
                    status=status.HTTP_403_FORBIDDEN
                )
            queryset = queryset.filter(device_id=device_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HourlyEnergyConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing hourly energy consumption
    """
    queryset = HourlyEnergyConsumption.objects.all()
    serializer_class = HourlyEnergyConsumptionSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('device_id', OpenApiTypes.UUID, description='Filter by device ID', required=True),
            OpenApiParameter('date', OpenApiTypes.DATE, description='Specific date (YYYY-MM-DD)', required=True),
        ]
    )
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get hourly consumption for a specific device and date"""
        device_id = request.query_params.get('device_id')
        date_str = request.query_params.get('date')
        
        if not device_id or not date_str:
            return Response(
                {'error': 'device_id and date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has access to this device
        accessible_device_ids = get_user_devices(request.user)
        if device_id not in [str(did) for did in accessible_device_ids]:
            return Response(
                {'error': 'You do not have access to this device'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get hourly data for the day
        hourly_data = HourlyEnergyConsumption.objects.filter(
            device_id=device_id,
            date=date
        ).order_by('hour')
        
        # Create complete 24-hour dataset (fill missing hours with 0)
        result = []
        hourly_dict = {item.hour: item for item in hourly_data}
        
        for hour in range(24):
            if hour in hourly_dict:
                item = hourly_dict[hour]
                result.append({
                    'hour': hour,
                    'total_consumption': item.total_consumption,
                    'measurement_count': item.measurement_count
                })
            else:
                result.append({
                    'hour': hour,
                    'total_consumption': 0.0,
                    'measurement_count': 0
                })
        
        return Response({
            'device_id': device_id,
            'date': date_str,
            'hourly_data': result,
            'total_daily_consumption': sum(item['total_consumption'] for item in result)
        })
    
    @extend_schema(
        parameters=[
            OpenApiParameter('device_id', OpenApiTypes.UUID, description='Filter by device ID', required=True),
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)', required=True),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)', required=True),
        ]
    )
    @action(detail=False, methods=['get'])
    def range(self, request):
        """Get consumption data for a date range"""
        device_id = request.query_params.get('device_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if not all([device_id, start_date_str, end_date_str]):
            return Response(
                {'error': 'device_id, start_date, and end_date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has access to this device
        accessible_device_ids = get_user_devices(request.user)
        if device_id not in [str(did) for did in accessible_device_ids]:
            return Response(
                {'error': 'You do not have access to this device'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get data for date range
        data = HourlyEnergyConsumption.objects.filter(
            device_id=device_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', 'hour')
        
        serializer = self.get_serializer(data, many=True)
        
        # Calculate total
        total = data.aggregate(total=Sum('total_consumption'))['total'] or 0.0
        
        return Response({
            'device_id': device_id,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'data': serializer.data,
            'total_consumption': total
        })


class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing synchronized devices
    Admin sees all devices, clients see only their assigned devices
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter devices based on user role"""
        user = self.request.user
        
        if user.role == 'admin':
            # Admin can see all devices
            return Device.objects.all()
        else:
            # Client can only see their assigned devices
            device_ids = UserDeviceMapping.objects.filter(
                user_id=user.id
            ).values_list('device_id', flat=True)
            return Device.objects.filter(id__in=device_ids)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing synchronized users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
