from flask import Flask, redirect, url_for
from config import config
from models import db, SensorData, Usuario
from mqtt_service import init_mqtt

from datetime import datetime, timedelta

# Importar Blueprints
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.monitor_routes import monitor_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Inicializar MQTT
    init_mqtt(app)
    
    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(monitor_bp)
    
    # Tarea programada para limpiar datos antiguos


    # Inicializar Scheduler
    from scheduler_service import init_scheduler
    init_scheduler(app)
    
    # Ruta raíz redirige según estado de sesión
    @app.route('/')
    def root():
        return redirect(url_for('monitor.index'))
        
    # Crear tablas si no existen e inicializar usuario admin
    with app.app_context():
        db.create_all()
        
        # Crear usuario admin si no existe
        if not Usuario.query.filter_by(email='admin@healthmonitor.com').first():
            admin = Usuario(
                nombre='Administrador',
                email='admin@healthmonitor.com',
                rol='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado")
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
