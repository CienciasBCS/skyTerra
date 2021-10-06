import os, requests

import flask_login
from flask import redirect, request, session, url_for, render_template_string, current_app
from app.models import User
from jose import jwt

from app.auth import bp

@bp.route('/login')
def login():

    session['csrf_state'] = os.urandom(8).hex()

    cognito_login = ("https://%s/login?response_type=code&client_id=%s&redirect_uri=%s/oauth2/authorize&state=%s" %
                     (current_app.config['COGNITO_DOMAIN'], current_app.config['COGNITO_CLIENT_ID'],
                      current_app.config['BASE_URL'], session['csrf_state']))

    return redirect(cognito_login)


@bp.route("/logout")
def logout():
    flask_login.logout_user()
    cognito_logout = ("https://%s/"
                      "logout?response_type=code&client_id=%s"
                      "&logout_uri=%s/" %
                      (current_app.config['COGNITO_DOMAIN'], current_app.config['COGNITO_CLIENT_ID'], 
                      current_app.config['BASE_URL']))
    print(cognito_logout)                      
    return redirect(cognito_logout)


@bp.route("/oauth2/authorize")
def callback():
    print(request.base_url)
    csrf_state = request.args.get('state')
    code = request.args.get('code')
    request_parameters = {'grant_type': 'authorization_code',
                          'client_id': current_app.config['COGNITO_CLIENT_ID'],
                          'code': code,
                          "redirect_uri": current_app.config['BASE_URL'] + "/oauth2/authorize"}
    response = requests.post("https://%s/oauth2/token" % current_app.config['COGNITO_DOMAIN'],
                             data=request_parameters,
                             auth=requests.auth.HTTPBasicAuth(current_app.config['COGNITO_CLIENT_ID'],
                                                              current_app.config['COGNITO_CLIENT_SECRET']))

    if response.status_code == requests.codes.ok and csrf_state == session['csrf_state']:
        verify(response.json()["access_token"])
        id_token = verify(
            response.json()["id_token"], response.json()["access_token"])
        user = User.query.filter_by(cog_user_id=id_token['cognito:username']).first()
        # user = User()
        session['email'] = id_token["email"]
        session['expires'] = id_token["exp"]
        session['refresh_token'] = response.json()["refresh_token"]
        flask_login.login_user(user, remember=True)
        if user.user_rol:
            if user.user_rol.tipo == 'gestor':
                return redirect(url_for("solarbeam_gestor.gestor_ofertas"))
            elif user.user_rol.tipo == 'comprador':
                return redirect(url_for("solarbeam_comprador.comprador_ofertas"))
            elif user.user_rol.tipo == 'integrador':
                return redirect(url_for("solarbeam_integrador.integrador_proyectos_disponibles"))
            elif user.user_rol.tipo == 'admin':
                return redirect(url_for("solarbeam_admin.pending_users"))                
        else:
            if user.tiene_rol == False:
                return redirect(url_for('solarbeam.estado_rol_usuario'))
            return redirect(url_for("solarbeam.confirmar_usuario"))

    return render_template_string("""
            <p>Something went wrong... {}</p>
            """.format(session['csrf_state']))


def verify(token, access_token=None):
    """Verify a cognito JWT"""

    JWKS_URL = ("https://cognito-idp.%s.amazonaws.com/%s/.well-known/jwks.json"
                % (current_app.config['AWS_REGION'], current_app.config['COGNITO_POOL_ID']))
    JWKS = requests.get(JWKS_URL).json()["keys"]

    header = jwt.get_unverified_header(token)
    key = [k for k in JWKS if k["kid"] == header['kid']][0]
    id_token = jwt.decode(
        token, key, audience=current_app.config['COGNITO_CLIENT_ID'], access_token=access_token)
    return id_token