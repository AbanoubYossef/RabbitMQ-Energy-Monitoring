
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .rabbitmq import get_publisher
import logging

logger = logging.getLogger(__name__)

# --- Helper for Admin Check ---
def is_admin(request):
    """Checks if the user role is 'admin'."""
    # Access from underlying Django request (set by middleware)
    django_request = getattr(request, '_request', request)
    return getattr(django_request, 'user_role', None) == 'admin'   

# ==============================================================================
# 1. CREATE USER (POST) - Admin Only
# ==============================================================================
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
        logger.info(f"User created in User Service: {user.id}")
        
        # Publish user_created event to RabbitMQ
        try:
            publisher = get_publisher()
            publisher.publish_user_created({
                'id': user.id,
                'username': user.username,
                'role': user.role
            })
            logger.info(f"Published user_created event for {user.username}")
        except Exception as e:
            logger.error(f"Failed to publish user_created event: {e}")
            # Don't fail the operation if RabbitMQ publish fails
        
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

# ==============================================================================
# 2. LIST USERS (GET) - Admin Only
# ==============================================================================
@api_view(['GET'])
def list_users(request):
    """
    List all users (Admin only)
    """
    if not is_admin(request):
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ==============================================================================
# 3. GET USER (GET) - Admin or Self
# ==============================================================================
@api_view(['GET'])
def get_user(request, user_id):
    """
    Get user by ID
    Admin can see all, Client can see only their own
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Check permissions: Admin OR client viewing their own profile
        django_request = getattr(request, '_request', request)
        user_id_from_token = getattr(django_request, 'user_id', None)
        if not is_admin(request) and str(user_id_from_token) != str(user_id):
            return Response(
                {'error': 'Permission denied. You can only view your own profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ==============================================================================
# 4. UPDATE USER (PUT) - Admin Only
# ==============================================================================
@api_view(['PUT'])
def update_user(request, user_id):
    """
    Update user (Admin ONLY - allows changing other users)
    """
    # Enforce Admin-Only Update
    if not is_admin(request):
        return Response(
            {'error': 'Admin permission required to update users.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Update fields
    for field, value in serializer.validated_data.items():
        setattr(user, field, value)
    
    user.save()
    logger.info(f"User updated in User Service: {user.id}")
    
    # Publish user_updated event to RabbitMQ
    try:
        publisher = get_publisher()
        publisher.publish_user_updated({
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
        logger.info(f"Published user_updated event for {user.username}")
    except Exception as e:
        logger.error(f"Failed to publish user_updated event: {e}")
    
    return Response({
        'message': 'User updated successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)

# ==============================================================================
# 5. DELETE USER (DELETE) - Admin Only
# ==============================================================================
@api_view(['DELETE'])
def delete_user(request, user_id):
    """
    Delete user (Admin ONLY - allows deleting other users)
    """
    # Enforce Admin-Only Delete
    if not is_admin(request):
        return Response(
            {'error': 'Admin permission required to delete users.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        logger.info(f"User deleted from User Service: {user_id}")
        
        # Publish user_deleted event to RabbitMQ
        try:
            publisher = get_publisher()
            publisher.publish_user_deleted(user_id)
            logger.info(f"Published user_deleted event for {user_id}")
        except Exception as e:
            logger.error(f"Failed to publish user_deleted event: {e}")
        
        return Response({
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ==============================================================================
# 6. ROLLBACK USER (DELETE) - Internal Saga
# ==============================================================================
@api_view(['DELETE'])
def rollback_user(request, user_id):
    """
    Rollback user creation (Saga compensation)
    """
    # This endpoint is typically secured internally (e.g., API Key, network policy)
    # and does not require a user role check.
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        logger.info(f"User rollback in User Service: {user_id}")
        
        return Response({
            'message': 'User rollback successful'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)