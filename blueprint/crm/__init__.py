from flask import Blueprint

webapp_crm = Blueprint('webapp_crm', __name__)

from .core import *