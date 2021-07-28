from app import create_app, db
from app.models import User, Licitacion, OfertaLicitacion

application = create_app()


@application.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Licitacion': Licitacion,
        'OfertaLicitacion': OfertaLicitacion
        }

if __name__ == '__main__':
    application.run(debug=True)