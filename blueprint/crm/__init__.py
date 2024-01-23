from flask import Blueprint, request, g
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

from .core import *