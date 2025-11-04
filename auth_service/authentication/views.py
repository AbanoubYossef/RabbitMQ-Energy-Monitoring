
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .saga import UserCreationSaga, UserUpdateSaga, UserDeletionSaga
import logging

logger = logging.getLogger(__name__)

def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    refresh['user_id'] = str(user.id)
    refresh['username'] = user.username
    refresh['role'] = user.role
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': str(user.id),
            'username': user.username,
            'role': user.role
        }
    }

@extend_schema(
    request=RegisterSerializer,
    responses={201: UserSerializer},
    description="Register a new user. Creates user in Auth, User, and Device services using Saga pattern.",
    examples=[
        OpenApiExample(
            'Register Example',
            value={
                'username': 'john',
                'password': 'password123',
                'role': 'client',
                'fname': 'John',
                'lname': 'Doe',
                'email': 'john@example.com',
                'phone': '+1234567890'
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register new user using Saga pattern
    Creates user in Auth, User, and Device services
    """
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Execute Saga
    saga = UserCreationSaga()
    success, result = saga.execute(serializer.validated_data)
    
    if not success:
        return Response(
            {'error': f'Registration failed: {result}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Generate tokens
    tokens = get_tokens_for_user(result)
    
    return Response({
        'message': 'User registered successfully',
        'tokens': tokens
    }, status=status.HTTP_201_CREATED)

@extend_schema(
    request=LoginSerializer,
    responses={200: dict},
    description="Login user and return JWT access and refresh tokens",
    examples=[
        OpenApiExample(
            'Admin Login',
            value={
                'username': 'admin',
                'password': 'admin123'
            }
        ),
        OpenApiExample(
            'Client Login',
            value={
                'username': 'alice',
                'password': 'alice123'
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return JWT token
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.check_password(password):
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    tokens = get_tokens_for_user(user)
    
    return Response({
        'message': 'Login successful',
        'tokens': tokens
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """
    Validate JWT token (used by other microservices)
    """
    user = request.user
    return Response({
        'valid': True,
        'user': {
            'id': str(user.id),
            'username': user.username,
            'role': user.role
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request, user_id):
    """
    Get user info by ID (used by other microservices)
    """
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    """
    Update user using Saga pattern
    Admin only or own account
    """
    # Check permissions
    if request.user.role != 'admin' and str(request.user.id) != user_id:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        saga = UserUpdateSaga(user_id)
        success, result = saga.execute(request.data)
        
        if not success:
            return Response(
                {'error': f'Update failed: {result}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = UserSerializer(result)
        return Response({
            'message': 'User updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """
    Delete user using Saga pattern
    Admin only
    """
    if request.user.role != 'admin':
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        User.objects.get(id=user_id)  # Check if exists
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    saga = UserDeletionSaga(user_id)
    success, message = saga.execute()
    
    if not success:
        return Response(
            {'error': message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': message
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    List all users (Admin only)
    """
    if request.user.role != 'admin':
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)