"""
Custom JWT Authentication for Monitoring Service
Handles JWT tokens without requiring database user lookup
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class SimpleUser:
    """
    Simple user object that holds JWT token claims.
    Does not require database lookup.
    """
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def __str__(self):
        return self.username


class MonitoringJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that doesn't require user lookup in database.
    The monitoring service only needs to verify the JWT token validity,
    not authenticate against a local user database.
    """
    
    def get_user(self, validated_token):
        """
        Returns a simple user object from the token claims.
        Does not perform database lookup.
        """
        try:
            user_id = validated_token.get('user_id')
            username = validated_token.get('username', 'unknown')
            role = validated_token.get('role', 'user')
            
            if user_id is None:
                raise InvalidToken('Token contained no recognizable user identification')
            
            # Create a simple user object without database lookup
            return SimpleUser(user_id, username, role)
            
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')
