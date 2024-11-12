import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth.models import User
from ninja.security import HttpBearer
from api.models import BlacklistedToken

class AuthHandler:
    @staticmethod
    def create_access_token(user: User, expiration_minutes: int = 1) -> str:
        """
        Create a JWT access token for a given user
        
        :param user: Django User instance
        :param expiration_minutes: Optional expiration time in minutes (default is 30)
        :return: JWT token string
        """
        exp_time = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'exp': exp_time
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token):
        """Verify and decode JWT token"""
        try:
            # First, check if token is blacklisted
            if BlacklistedToken.is_blacklisted(token):
                return None
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# Bearer Authentication
class BearerAuth(HttpBearer):
    def authenticate(self, request, token):
        """
        Token authentication method
        
        :param request: Incoming HTTP request
        :param token: Bearer token from Authorization header
        :return: Authenticated user or None
        """
        decoded = AuthHandler.verify_token(token)
        if decoded:
            try:
                user = User.objects.get(id=decoded.get('user_id'))
                return user
            except User.DoesNotExist:
                return None
        return None