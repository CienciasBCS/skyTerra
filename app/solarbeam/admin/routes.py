from flask import render_template

from app.decorators import login_required_roles
from . import bp

@bp.route('/usuarios_por_confirmar')
@login_required_roles(['admin'])
def confirm_users():

    return  render_template('solarbeam/admin/usuarios_por_confirmar.html')