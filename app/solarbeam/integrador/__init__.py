from flask import Blueprint

bp = Blueprint('solarbeam_integrador', __name__, url_prefix='/solarbeam/app/integrador')

from . import routes