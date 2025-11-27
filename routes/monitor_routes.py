"""
Rutas para el monitor en tiempo real y estadísticas
"""
from flask import Blueprint, render_template, jsonify, request, session
from controllers.monitor_controller import MonitorController
from controllers.patient_controller import PatientController
from mqtt_service import get_current_readings
from utils import login_required

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/')
@login_required
def index():
    """Vista principal del monitor en tiempo real"""
    paciente_activo = MonitorController.get_active_patient()
    todos_pacientes = PatientController.get_all_patients()
    
    return render_template('index.html', 
                         user_name=session.get('user_name', 'Usuario'),
                         paciente=paciente_activo,
                         pacientes=todos_pacientes)

@monitor_bp.route('/<int:patient_id>')
@login_required
def monitor_patient(patient_id):
    """Vista de monitoreo para un paciente específico"""
    paciente = PatientController.get_patient_by_id(patient_id)
    todos_pacientes = PatientController.get_all_patients()
    
    return render_template('index.html', 
                         user_name=session.get('user_name', 'Usuario'),
                         paciente=paciente,
                         pacientes=todos_pacientes)

@monitor_bp.route('/datos')
@login_required
def get_data():
    """API para obtener datos en tiempo real e históricos"""
    range_param = request.args.get('range', '5min')
    paciente_id = request.args.get('paciente_id')
    
    records = MonitorController.get_sensor_data(range_param, paciente_id)
    current_readings = get_current_readings()
    
    # Identificar el paciente que se está visualizando
    paciente_visualizado = None
    if paciente_id:
        paciente_visualizado = PatientController.get_patient_by_id(paciente_id)
    else:
        paciente_visualizado = MonitorController.get_active_patient()

    # Verificar correspondencia de device_id
    # Solo mostramos datos en tiempo real si el device_id de las lecturas actuales coincide con el del paciente visualizado
    readings_device_id = current_readings.get('device_id')
    patient_device_id = paciente_visualizado.device_id if paciente_visualizado else None
    
    print(f"DEBUG: Checking device match. Readings ID: {readings_device_id}, Patient ID: {patient_device_id}, Patient Name: {paciente_visualizado.nombre if paciente_visualizado else 'None'}")
    
    show_live_data = False
    if readings_device_id and patient_device_id and readings_device_id == patient_device_id:
        show_live_data = True
        print("DEBUG: Device IDs match. Showing live data.")
    else:
        print("DEBUG: Device IDs DO NOT match or missing. Hiding live data.")
        
    if not show_live_data:
        # Si los device_id no coinciden, limpiamos las lecturas actuales para que se muestre el valor por defecto (1)
        current_readings = {
            'temperature': None,
            'heart_rate': None,
            'spo2': None,
            'last_update': None,
            'device_id': None
        }
    
    data = MonitorController.format_sensor_data(records, current_readings)
    
    return jsonify(data)

@monitor_bp.route('/stats')
@login_required
def stats():
    """Vista de estadísticas globales (Dashboard)"""
    stats_data = MonitorController.get_global_stats()
    return render_template('stats.html', stats=stats_data)

@monitor_bp.route('/api/stats')
@login_required
def api_stats():
    """API para datos estadísticos"""
    days = int(request.args.get('days', 7))
    patient_id = request.args.get('patient_id')
    data = MonitorController.get_stats_data(days, patient_id)
    return jsonify(data)
