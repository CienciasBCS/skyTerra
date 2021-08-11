from flask import Blueprint

bp = Blueprint('solarbeam_api', __name__, url_prefix='/solarbeam/api')

from . import routes