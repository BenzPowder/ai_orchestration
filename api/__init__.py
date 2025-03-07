from flask import Blueprint

api = Blueprint('api', __name__)

from . import webhook_routes
from . import agent_routes
