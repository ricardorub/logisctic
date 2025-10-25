from .db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # ← Añade esta línea
    
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

class CrudItem(db.Model):
    __tablename__ = 'crud_items'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable=False)
    numero_pedidos = db.Column(db.Integer, nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)
    frecuencia = db.Column(db.String(100), nullable=False)
    stock_unidades = db.Column(db.Integer, nullable=False)
    ventas = db.Column(db.Float, nullable=False)
    cobertura = db.Column(db.Float, nullable=False)
    fecha_pedido = db.Column(db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    tiempo_entrega = db.Column(db.Integer, nullable=False)
    proveedor = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<CrudItem {self.item}>'

class SandboxItem(db.Model):
    __tablename__ = 'sandbox_items'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable=False)
    numero_pedidos = db.Column(db.Integer, nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)
    frecuencia = db.Column(db.String(100), nullable=False)
    stock_unidades = db.Column(db.Integer, nullable=False)
    ventas = db.Column(db.Float, nullable=False)
    cobertura = db.Column(db.Float, nullable=False)
    fecha_pedido = db.Column(db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    tiempo_entrega = db.Column(db.Integer, nullable=False)
    proveedor = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<SandboxItem {self.item}>'