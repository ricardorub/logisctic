from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), default='medico')  # admin, medico, enfermero
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    device_id = db.Column(db.String(50), unique=True, nullable=True)
    foto_url = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.String(50), default='normal')  # normal, advertencia, critico
    ultima_visita = db.Column(db.DateTime, default=datetime.now)
    notas = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    
    # Relación con lecturas de sensores
    lecturas = db.relationship('SensorData', backref='paciente', lazy=True)
    # Relación con notificaciones
    notificaciones = db.relationship('Notificacion', backref='paciente', lazy=True, cascade="all, delete-orphan")

class SensorData(db.Model):
    __tablename__ = 'temperatura'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=True)
    valor = db.Column(db.Float, nullable=False)
    heart_rate = db.Column(db.Integer, nullable=True)
    spo2 = db.Column(db.Integer, nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.now, index=True)

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    job_id = db.Column(db.String(100), nullable=True)
    enviado = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
