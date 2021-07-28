from functools import wraps
from flask import current_app
from flask_login import current_user

def login_required_roles(perm_roles="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized() 
            if (current_user.user_rol.tipo not in perm_roles) and ("ANY" not in perm_roles):
                return current_app.login_manager.unauthorized() 
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


def login_required_no_rol():
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            elif current_user.tiene_rol:
                return current_app.login_manager.unauthorized() 
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper