"""
Configuración de la aplicación Flask
"""
import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here_change_in_production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/temperatura_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración MQTT
    MQTT_BROKER = os.environ.get('MQTT_BROKER') or 'broker.emqx.io'
    MQTT_PORT = int(os.environ.get('MQTT_PORT') or 1883)
    MQTT_TOPIC = 'healthmonitor/#'
    
    # Configuración de datos
    DATA_VALIDITY_TIMEOUT = 30000  # 30 segundos en milisegundos
    OLD_DATA_RETENTION_DAYS = 30  # Días para mantener datos antiguos

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
