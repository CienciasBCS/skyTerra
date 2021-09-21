from flask import Blueprint

bp = Blueprint('solarbeam_gestor', __name__, url_prefix='/solarbeam/app/gestor')

from . import routes