from flask import render_template
from flask_login import current_user

from app.main import bp

@bp.route('/')
def home():
    print(current_user.is_authenticated)
    return render_template('pages/index.html')