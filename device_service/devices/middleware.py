"""
JWT Token validation middleware
"""
import jwt
from django.conf import settings
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    """
    Middleware to validate JWT tokens from Auth service
    """
    
    # Endpoints that don't require authentication
    EXEMPT_PATHS = [
        '/api/users/create/',           # Called by Auth service during Saga
        '/api/users/',                  # For internal service calls
        '/rollback/',                   # For Saga compensation
        '/admin/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if path is exempt
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return self.get_response(request)
        
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'No token provided'}, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Attach user info to request
            request.user_id = payload.get('user_id')
            request.username = payload.get('username')
            request.user_role = payload.get('role')
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return self.get_response(request)