from flask import Blueprint

bp = Blueprint('solarbeam_comprador', __name__, url_prefix='/solarbeam/app/comprador')

from . import routes