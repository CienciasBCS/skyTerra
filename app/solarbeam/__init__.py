from flask import Blueprint

bp = Blueprint('solarbeam', __name__)

from . import routes