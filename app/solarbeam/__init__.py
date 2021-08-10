from flask import Blueprint

bp = Blueprint('solarbeam', __name__, url_prefix='/solarbeam/app')

from . import routes