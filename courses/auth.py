# auth.py
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from ninja.security import HttpBearer
from django.shortcuts import get_object_or_404
from .models import User

SECRET_KEY = settings.SECRET_KEY

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = get_object_or_404(User, id=payload['user_id'])
            return user 
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def create_access_token(user_id: int):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")