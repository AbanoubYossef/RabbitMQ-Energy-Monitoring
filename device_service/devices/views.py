from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Device, UserDeviceMapping
from .serializers import (
    UserSerializer, DeviceSerializer, DeviceCreateSerializer,
    UserDeviceMappingSerializer, AssignDeviceSerializer, UserCreateSerializer
)
import logging

logger = logging.getLogger(__name__)

# ========== USER ENDPOINTS (For Saga) ==========
# --- Helper for Admin Check ---
def is_admin(request):
    """Checks if the user role is 'admin'."""
    return getattr(request, 'user_role', None) == 'admin'       
@api_view(['POST'])
def create_user(request):
    """
    Create user (called by Auth service during Saga)
    No authentication required - internal service call
    """
    serializer = UserCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create(**serializer.validated_data)
        logger.info(f"User created in Device Service: {user.id}")
        
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"User creation failed: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['PUT'])
def update_user(request, user_id):
    """
    Update user (called by Auth service during Saga, now REQUIRES ADMIN token)
    """
    if not is_admin(request): # <-- ADDED CHECK
        return Response(
            {'error': 'Admin permission required for user synchronization.'},
            status=status.HTTP_403_FORBIDDEN
        )
        
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'username' in request.data:
        user.username = request.data['username']
    if 'role' in request.data:
        user.role = request.data['role']
    
    user.save()
    logger.info(f"User updated in Device Service: {user.id}")
    
    return Response({
        'message': 'User updated successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_user(request, user_id):
    """
    Delete user and all mappings (called by Auth service during Saga, now REQUIRES ADMIN token)
    """
    if not is_admin(request): # <-- ADDED CHECK
        return Response(
            {'error': 'Admin permission required for user synchronization.'},
            status=status.HTTP_403_FORBIDDEN
        )
        
    try:
        user = User.objects.get(id=user_id)
        # Cascade delete will handle UserDeviceMapping
        user.delete()
        logger.info(f"User deleted from Device Service: {user_id}")
        
        return Response({
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def rollback_user(request, user_id):
    """
    Rollback user creation (Saga compensation, now REQUIRES ADMIN token)
    """
    if not is_admin(request): # <-- ADDED CHECK
        return Response(
            {'error': 'Admin permission required for user synchronization.'},
            status=status.HTTP_403_FORBIDDEN
        )
        
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        logger.info(f"User rollback in Device Service: {user_id}")
        
        return Response({
            'message': 'User rollback successful'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ========== DEVICE ENDPOINTS ==========

@api_view(['POST'])
def create_device(request):
    """
    Create device (Admin only)
    """
    if request.user_role != 'admin':
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = DeviceCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        device = Device.objects.create(**serializer.validated_data)
        logger.info(f"Device created: {device.id}")
        
        return Response({
            'message': 'Device created successfully',
            'device': DeviceSerializer(device).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Device creation failed: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def list_devices(request):
    """
    List devices
    Admin: see all devices
    Client: see only their devices
    """
    if request.user_role == 'admin':
        devices = Device.objects.all()
    else:
        # Get devices assigned to this user
        user = User.objects.get(id=request.user_id)
        device_ids = UserDeviceMapping.objects.filter(user=user).values_list('device_id', flat=True)
        devices = Device.objects.filter(id__in=device_ids)
    
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_device(request, device_id):
    """
    Get device by ID
    Admin can see all, Client can see only their own
    """
    try:
        device = Device.objects.get(id=device_id)
        
        # Check permissions for clients
        if request.user_role == 'client':
            try:
                mapping = UserDeviceMapping.objects.get(device=device, user_id=request.user_id)
            except UserDeviceMapping.DoesNotExist:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = DeviceSerializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_device(request, device_id):
    """
    Update device (Admin only)
    """
    if request.user_role != 'admin':
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        device = Device.objects.get(id=device_id)
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = DeviceCreateSerializer(data=request.data, partial=True)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Update fields
    for field, value in serializer.validated_data.items():
        setattr(device, field, value)
    
    device.save()
    logger.info(f"Device updated: {device.id}")
    
    return Response({
        'message': 'Device updated successfully',
        'device': DeviceSerializer(device).data
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_device(request, device_id):
    """
    Delete device (Admin only)
    """
    if request.user_role != 'admin':
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        device = Device.objects.get(id=device_id)
        # Cascade delete will handle UserDeviceMapping
        device.delete()
        logger.info(f"Device deleted: {device_id}")
        
        return Response({
            'message': 'Device deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

# ========== DEVICE ASSIGNMENT ENDPOINTS ==========

@api_view(['POST'])
def assign_device(request):
    """
    Assign device to user (Admin only)
    Multiple users can share the same device
    """
    if request.user_role != 'admin':
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AssignDeviceSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    device_id = serializer.validated_data['device_id']
    user_id = serializer.validated_data['user_id']
    
    try:
        device = Device.objects.get(id=device_id)
        user = User.objects.get(id=user_id)
        
        # Check if this specific user-device mapping already exists
        if UserDeviceMapping.objects.filter(device=device, user=user).exists():
            return Response(
                {'error': 'Device is already assigned to this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create mapping (multiple users can have the same device)
        mapping = UserDeviceMapping.objects.create(user=user, device=device)
        logger.info(f"Device {device_id} assigned to user {user_id}")
        
        return Response({
            'message': 'Device assigned successfully',
            'mapping': UserDeviceMappingSerializer(mapping).data
        }, status=status.HTTP_201_CREATED)
        
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Device assignment failed: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def unassign_device(request, device_id):
    """
    Unassign device from a specific user (Admin only)
    Requires user_id in request body or query params
    """
    if request.user_role != 'admin':
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get user_id from query params or request body
    user_id = request.query_params.get('user_id') or request.data.get('user_id')
    
    if not user_id:
        return Response(
            {'error': 'user_id is required to unassign device'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        mapping = UserDeviceMapping.objects.get(device_id=device_id, user_id=user_id)
        mapping.delete()
        logger.info(f"Device {device_id} unassigned from user {user_id}")
        
        return Response({
            'message': 'Device unassigned successfully'
        }, status=status.HTTP_200_OK)
        
    except UserDeviceMapping.DoesNotExist:
        return Response({'error': 'Device mapping not found for this user'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_user_devices(request, user_id):
    """
    Get all devices for a specific user
    Admin can see all, Client can see only their own
    """
    # Check permissions
    if request.user_role != 'admin' and str(request.user_id) != str(user_id):
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(id=user_id)
        mappings = UserDeviceMapping.objects.filter(user=user).select_related('device')
        
        devices = [mapping.device for mapping in mappings]
        serializer = DeviceSerializer(devices, many=True)
        
        return Response({
            'user': UserSerializer(user).data,
            'devices': serializer.data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_mappings(request):
    """
    List device-user mappings
    Admin: see all mappings
    Client: see only their own mappings
    """
    if request.user_role == 'admin':
        mappings = UserDeviceMapping.objects.all()
    else:
        # Clients can only see their own mappings
        mappings = UserDeviceMapping.objects.filter(user_id=request.user_id)
    
    serializer = UserDeviceMappingSerializer(mappings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)