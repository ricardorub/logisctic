"""
Servicio MQTT para manejar la conexión y recepción de datos
"""
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from models import db, SensorData, Paciente
from flask import current_app

# Variables globales para lecturas actuales
current_readings = {
    'temperature': None,
    'heart_rate': None,
    'spo2': None,
    'last_update': None
}

def init_mqtt(app):
    """Inicializa el cliente MQTT"""
    client = mqtt.Client()
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Connected successfully")
            client.subscribe(app.config['MQTT_TOPIC'])
        else:
            print(f"Failed to connect, return code {rc}")
    
    def on_message(client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            data = json.loads(payload)
            
            print(f"Received message on {topic}: {data}")
            
            # Actualizar lecturas actuales
            if 'temperature' in data and data['temperature'] is not None:
                current_readings['temperature'] = float(data['temperature'])
            if 'hr' in data and data['hr'] is not None:
                current_readings['heart_rate'] = int(data['hr'])
            if 'spo2' in data and data['spo2'] is not None:
                current_readings['spo2'] = int(data['spo2'])
            
            current_readings['last_update'] = datetime.now()
            
            # Guardar en base de datos si tenemos todos los datos
            if None not in [current_readings['temperature'], current_readings['heart_rate'], current_readings['spo2']]:
                with app.app_context():
                    # Obtener paciente por device_id si viene en el mensaje, sino buscar el activo
                    device_id = data.get('device_id')
                    paciente = None
                    
                    if device_id:
                        paciente = Paciente.query.filter_by(device_id=device_id).first()
                    
                    if not paciente:
                        # Fallback: buscar paciente activo (comportamiento anterior)
                        paciente = Paciente.query.filter_by(activo=True).first()
                    
                    record = SensorData(
                        paciente_id=paciente.id if paciente else None,
                        valor=current_readings['temperature'],
                        heart_rate=current_readings['heart_rate'],
                        spo2=current_readings['spo2']
                    )
                    db.session.add(record)
                    db.session.commit()
                    print(f"Datos guardados para paciente: {paciente.nombre if paciente else 'Desconocido'}")
                    
        except json.JSONDecodeError:
            print(f"Error decoding JSON from payload: {payload}")
        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'], 60)
        client.loop_start()
        global mqtt_client
        mqtt_client = client
        return client
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        return None

def get_current_readings():
    """Retorna las lecturas actuales"""
    return current_readings

def publish_message(topic, message):
    """Publica un mensaje en el tópico especificado"""
    if mqtt_client:
        mqtt_client.publish(topic, message)
        print(f"Published message to {topic}: {message}")
        return True
    return False
