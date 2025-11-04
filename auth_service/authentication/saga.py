"""
Saga Pattern with Compensation for distributed transactions
"""
import requests
import logging
from django.conf import settings
from .models import User

logger = logging.getLogger(__name__)

class UserCreationSaga:
    """
    Saga pattern for creating user across all microservices
    Steps:
    1. Create user in Auth DB
    2. Create user in User Service
    3. Create user in Device Service
    If any step fails, compensate (rollback) previous steps
    """
    
    def __init__(self):
        self.user_id = None
        self.auth_created = False
        self.user_service_created = False
        self.device_service_created = False
    
    def execute(self, user_data):
        """Execute saga steps"""
        try:
            # Step 1: Create in Auth DB
            user = self._create_auth_user(user_data)
            self.user_id = str(user.id)
            self.auth_created = True
            
            # Step 2: Create in User Service
            self._create_user_service(user, user_data)
            self.user_service_created = True
            
            # Step 3: Create in Device Service
            self._create_device_service(user)
            self.device_service_created = True
            
            return True, user
            
        except Exception as e:
            logger.error(f"Saga failed: {str(e)}")
            self._compensate()
            return False, str(e)
    
    def _create_auth_user(self, user_data):
        """Step 1: Create user in Auth DB"""
        user = User(
            username=user_data['username'],
            role=user_data.get('role', 'client')
        )
        user.set_password(user_data['password'])
        user.save()
        logger.info(f"Auth user created: {user.id}")
        return user
    
    def _create_user_service(self, user, user_data):
        """Step 2: Create user in User Service"""
        payload = {
            'id': str(user.id),
            'username': user.username,
            'role': user.role,
            'fname': user_data.get('fname', ''),
            'lname': user_data.get('lname', ''),
            'email': user_data.get('email', ''),
            'phone': user_data.get('phone', '')
        }
        
        try:
            response = requests.post(
                f"{settings.USER_SERVICE_URL}/users/create/",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"User service created: {user.id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"User service creation failed: {str(e)}")
            raise Exception(f"User service failed: {str(e)}")
    
    def _create_device_service(self, user):
        """Step 3: Create user in Device Service"""
        payload = {
            'id': str(user.id),
            'username': user.username,
            'role': user.role
        }
        
        try:
            response = requests.post(
                f"{settings.DEVICE_SERVICE_URL}/users/create/",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Device service created: {user.id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Device service creation failed: {str(e)}")
            raise Exception(f"Device service failed: {str(e)}")
    
    def _compensate(self):
        """Rollback all completed steps"""
        logger.warning(f"Starting compensation for user: {self.user_id}")
        
        # Rollback Device Service
        if self.device_service_created:
            self._rollback_device_service()
        
        # Rollback User Service
        if self.user_service_created:
            self._rollback_user_service()
        
        # Rollback Auth DB
        if self.auth_created:
            self._rollback_auth_user()
    
    def _rollback_auth_user(self):
        """Delete user from Auth DB"""
        try:
            User.objects.filter(id=self.user_id).delete()
            logger.info(f"Auth user rolled back: {self.user_id}")
        except Exception as e:
            logger.error(f"Auth rollback failed: {str(e)}")
    
    def _rollback_user_service(self):
        """Delete user from User Service"""
        try:
            requests.delete(
                f"{settings.USER_SERVICE_URL}/users/{self.user_id}/rollback/",
                timeout=5
            )
            logger.info(f"User service rolled back: {self.user_id}")
        except Exception as e:
            logger.error(f"User service rollback failed: {str(e)}")
    
    def _rollback_device_service(self):
        """Delete user from Device Service"""
        try:
            requests.delete(
                f"{settings.DEVICE_SERVICE_URL}/users/{self.user_id}/rollback/",
                timeout=5
            )
            logger.info(f"Device service rolled back: {self.user_id}")
        except Exception as e:
            logger.error(f"Device service rollback failed: {str(e)}")


class UserUpdateSaga:
    """Saga for updating user across all services"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.old_auth_data = None
        self.old_user_data = None
        self.old_device_data = None
    
    def execute(self, update_data):
        """Execute update saga"""
        try:
            # Backup current data
            user = User.objects.get(id=self.user_id)
            self.old_auth_data = {
                'username': user.username,
                'role': user.role
            }
            
            # Update Auth DB
            if 'username' in update_data:
                user.username = update_data['username']
            if 'role' in update_data:
                user.role = update_data['role']
            if 'password' in update_data:
                user.set_password(update_data['password'])
            user.save()
            
            # Update User Service
            self._update_user_service(update_data)
            
            # Update Device Service
            self._update_device_service(update_data)
            
            return True, user
            
        except Exception as e:
            logger.error(f"Update saga failed: {str(e)}")
            self._compensate()
            return False, str(e)
    
    def _update_user_service(self, update_data):
        """Update in User Service"""
        try:
            response = requests.put(
                f"{settings.USER_SERVICE_URL}/users/{self.user_id}/update/",
                json=update_data,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"User service update failed: {str(e)}")
    
    def _update_device_service(self, update_data):
        """Update in Device Service"""
        try:
            payload = {k: v for k, v in update_data.items() if k in ['username', 'role']}
            response = requests.put(
                f"{settings.DEVICE_SERVICE_URL}/users/{self.user_id}/update/",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Device service update failed: {str(e)}")
    
    def _compensate(self):
        """Restore old data"""
        if self.old_auth_data:
            user = User.objects.get(id=self.user_id)
            user.username = self.old_auth_data['username']
            user.role = self.old_auth_data['role']
            user.save()


class UserDeletionSaga:
    """Saga for deleting user across all services"""
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    def execute(self):
        """Execute deletion saga"""
        try:
            # Delete from Device Service first (has foreign keys)
            self._delete_device_service()
            
            # Delete from User Service
            self._delete_user_service()
            
            # Delete from Auth DB
            User.objects.filter(id=self.user_id).delete()
            
            return True, "User deleted successfully"
            
        except Exception as e:
            logger.error(f"Deletion saga failed: {str(e)}")
            return False, str(e)
    
    def _delete_user_service(self):
        """Delete from User Service"""
        try:
            response = requests.delete(
                f"{settings.USER_SERVICE_URL}/users/{self.user_id}/",
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"User service deletion failed: {str(e)}")
    
    def _delete_device_service(self):
        """Delete from Device Service"""
        try:
            response = requests.delete(
                f"{settings.DEVICE_SERVICE_URL}/users/{self.user_id}/",
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Device service deletion failed: {str(e)}")