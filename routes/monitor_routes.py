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
    
    # Verificar si el paciente solicitado es el activo para mostrar datos en tiempo real
    paciente_activo = MonitorController.get_active_patient()
    is_active = False
    if paciente_activo and paciente_id:
        is_active = str(paciente_activo.id) == str(paciente_id)
    elif paciente_activo and not paciente_id:
        is_active = True
        
    # Si no es el paciente activo, no usamos las lecturas actuales (que son globales)
    if not is_active:
        print(f"DEBUG: Patient {patient_id} is NOT active (active is {paciente_activo.id if paciente_activo else 'None'}). Clearing current readings.")
        current_readings = {
            'temperature': None,
            'heart_rate': None,
            'spo2': None,
            'last_update': None
        }
    else:
        print(f"DEBUG: Patient {patient_id} IS active. Using live readings.")
    
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
