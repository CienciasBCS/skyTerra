from flask import render_template
from flask_login import current_user

from app.main import bp

@bp.route('/')
def home():
    
    return render_template('static_pages/custom/index.html')
    
@bp.route('/usuario_final/')
def usuario_final():

    return render_template('static_pages/custom/usuario_final.html')

@bp.route('/como_funciona/')
def como_funciona():

    return render_template('static_pages/custom/como_funciona.html')