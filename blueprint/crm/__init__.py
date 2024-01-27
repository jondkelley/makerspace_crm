from flask import Blueprint, request, g
from functools import wraps
from flask import make_response
webapp_crm = Blueprint('webapp_crm', __name__)

@webapp_crm.context_processor
def inject_user_roles():
    """
    In Flask, to automatically include certain variables (like is_admin and roles) in all renderings of templates,
    you can use the context_processor decorator.
    """
    user_id = request.cookies.get('user_id')
    if user_id:
        user = PersonCredentials.get_or_none(PersonCredentials.user_id == user_id)
        if user:
            roles = [role.role for role in PersonRbac.select().where((PersonRbac.person == user.person) & (PersonRbac.permission == True))]
            is_admin = PersonRbac.get_or_none((PersonRbac.person == user.person) & (PersonRbac.role == 'admin') & (PersonRbac.permission == True))
            return {'is_admin': bool(is_admin), 'roles': roles}
    return {}


def requires_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        if user_id:
            user = PersonCredentials.get_or_none(PersonCredentials.user_id == user_id)
            if user:
                is_admin = PersonRbac.get_or_none(
                    (PersonRbac.person == user.person) & 
                    (PersonRbac.role == 'admin') & 
                    (PersonRbac.permission == True)
                )
                if is_admin:
                    return f(*args, **kwargs)
        
        return make_response("Forbidden", 403)
    return decorated_function


from .core import *