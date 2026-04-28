# permissions.py
from ninja.errors import HttpError
from functools import wraps

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.auth:
                raise HttpError(401, "Unauthorized")
            if request.auth.role not in allowed_roles:
                raise HttpError(403, "Forbidden: You don't have permission")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

is_instructor = role_required(['instructor', 'admin'])
is_admin = role_required(['admin'])
is_student = role_required(['student', 'admin'])