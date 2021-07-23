from flask_login import UserMixin

from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cog_user_id = db.Column(db.String(50), unique=True)
    nombre = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(10), unique=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))

    def __repr__(self):
        return f'<User {self.username}>'  

class Rol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(25))

    def __repr__(self):
        return f'<Rol {self.nombre}>'  

class Marca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(75), nullable=False)
    productos = db.relationship('Producto', backref='marca')

    def __repr__(self):
        return f'<Marca: {self.nombre}>'    

class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'))
    type = db.Column(db.String(50))
    paneles = db.relationship('Panel', backref='producto')
    inversores = db.relationship('Inversor', backref='producto')

    __mapper_args__ = {
        'polymorphic_identity':'producto',
        'polymorphic_on': type
    }

class Panel(Producto):
    __tablename__ = 'panel'
    id = db.Column(db.Integer, db.ForeignKey('producto.id'), primary_key=True)
    modelo = db.Column(db.String(100),  nullable=False)
    ficha_tecnica_key = db.Column(db.String(50), nullable=False)
    wp = db.Column(db.Integer, nullable=False)
    vmp = db.Column(db.Numeric(4, 2), nullable=False)
    imp = db.Column(db.Numeric(4, 2), nullable=False)
    efc = db.Column(db.Numeric(4, 2), nullable=False)

    def __repr__(self):
        return f'<Panel: {self.marca.nombre} - wp: {self.wp}>'  

    __mapper_args__ = {
        'polymorphic_identity':'panel',
    }

class Inversor(Producto):
    id = db.Column(db.Integer, db.ForeignKey('producto.id'), primary_key=True)
    modelo = db.Column(db.String(100),  nullable=False)
    ficha_tecnica_key = db.Column(db.String(50), nullable=False)
    min_wp = db.Column(db.Integer, nullable=False)
    max_wp = db.Column(db.Integer, nullable=False)
    kw_ac = db.Column(db.Integer, nullable=False)
    max_vdc = db.Column(db.Numeric(4, 2), nullable=False)
    max_isc = db.Column(db.Numeric(4, 2), nullable=False)
    max_imc = db.Column(db.Numeric(4, 2), nullable=False)
    min_mppt = db.Column(db.Numeric(4, 2), nullable=False)
    max_mppt = db.Column(db.Numeric(4, 2), nullable=False)
    num_mppt = db.Column(db.Integer, nullable=False)
    strings = db.Column(db.Integer, nullable=False)
    efc = db.Column(db.Numeric(4, 2), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'inversor',
    }

class licitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kwh = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Licitación de: {self.user.nombre} - kwh: {self.kwh}>'  

class OfertaProveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    licitacion_id = db.Column(db.Integer, db.ForeignKey('licitacion.id'), nullable=False)
    num_max = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(8, 2),  nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Oferta: {self.producto.type} Para: {self.licitacion.user.nombre}>'  

class OfertaCondicionada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oferta_1 = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), nullable=False)
    oferta_2 = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), nullable=False)


class OfertaGrupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class OfertaExcluyente(db.Model):
    grupo_id = db.Column(db.Integer, db.ForeignKey('oferta_grupo.id'), primary_key=True)
    oferta = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), primary_key=True)

class OfertaLicitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    licitacion_id = db.Column(db.Integer, db.ForeignKey('licitacion.id'))
    comprador_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    min_kw = db.Column(db.Numeric(4, 2),  nullable=False)
    max_kw = db.Column(db.Numeric(4, 2),  nullable=False)
    min_wp = db.Column(db.Numeric(4, 2),  nullable=False)
    max_wp = db.Column(db.Numeric(4, 2),  nullable=False)
    precio_max = db.Column(db.Numeric(12, 2),  nullable=False)
    

@login.user_loader
def load_user(cog_user_id):
    return User.query.get(cog_user_id)