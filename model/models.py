from .db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f'<Contact {self.name} - {self.subject}>'


class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, unique=True, nullable=False)
    proveedor = db.Column(db.String(100), nullable=False)
    nombre_producto = db.Column(db.String(100), nullable=False)
    cantidad_proveedor = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    sku = db.Column(db.String(6))
    
    # --- INICIO DE LA MODIFICACIÓN ---
    # Esta es la relación que define el borrado en cascada
    # basado en el `compra_id`.
    inventario = db.relationship(
        'Inventario',
        primaryjoin='Compra.compra_id == Inventario.compra_id',
        foreign_keys='[Inventario.compra_id]',
        backref='compra',
        cascade='all, delete',
        uselist=False
    )
    # --- FIN DE LA MODIFICACIÓN ---

    def __repr__(self):
        return f'<Compra {self.id}>'


class Inventario(db.Model):
    __tablename__ = 'inventario'
    id = db.Column(db.Integer, primary_key=True)
    # La clave foránea apunta a la columna `compra_id` de la tabla `compras`
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.compra_id'), nullable=False)
    proveedor = db.Column(db.String(100), nullable=False)
    nombre_producto = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    cantidad_total = db.Column(db.Integer, nullable=False)
    fecha_recepcion = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Inventario {self.id}>'


class Reposicion(db.Model):
    __tablename__ = 'reposiciones'
    id = db.Column(db.Integer, primary_key=True)
    reposicion_id = db.Column(db.Integer, unique=True, nullable=False)
    sku = db.Column(db.String(100), nullable=False)
    nombre_producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    tienda = db.Column(db.String(100), nullable=False)
    fecha_reposicion = db.Column(db.Date, nullable=False)
    fecha_despacho = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Reposicion {self.id}>'
