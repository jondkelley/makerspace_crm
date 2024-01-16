from flask import Blueprint

webapp_main = Blueprint('webapp_main', __name__)

from .core import *