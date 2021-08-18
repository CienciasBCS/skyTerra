from flask import Blueprint

bp = Blueprint('solarbeam_admin', __name__, url_prefix='/solarbeam/app/admin')

from . import routes