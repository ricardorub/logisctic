"""
Rutas para gestión de pacientes
"""
from flask import Blueprint, render_template, request, jsonify
from controllers.patient_controller import PatientController
from utils import login_required

patient_bp = Blueprint('patients', __name__)

@patient_bp.route('/patients')
@login_required
def index():
    """Vista principal de lista de pacientes"""
    pacientes = PatientController.get_all_patients()
    stats = PatientController.get_patients_stats()
    
    return render_template('patients.html', 
                         pacientes=pacientes,
                         total_pacientes=stats['total'],
                         pacientes_normales=stats['normales'],
                         pacientes_advertencia=stats['advertencia'],
                         pacientes_criticos=stats['criticos'])

# API Endpoints

@patient_bp.route('/api/pacientes', methods=['POST'])
@login_required
def create_patient():
    """Crear nuevo paciente"""
    try:
        data = request.json
        paciente = PatientController.create_patient(data)
        return jsonify({'message': 'Paciente creado exitosamente', 'id': paciente.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@patient_bp.route('/api/pacientes/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_patient(id):
    """Gestionar un paciente específico (Ver, Editar, Eliminar)"""
    try:
        if request.method == 'GET':
            paciente = PatientController.get_patient_by_id(id)
            return jsonify({
                'id': paciente.id,
                'nombre': paciente.nombre,
                'edad': paciente.edad,
                'email': paciente.email,
                'telefono': paciente.telefono,
                'device_id': paciente.device_id,
                'estado': paciente.estado,
                'ultima_visita': paciente.ultima_visita.isoformat() if paciente.ultima_visita else None,
                'notas': paciente.notas,
                'foto_url': paciente.foto_url
            })
        
        elif request.method == 'PUT':
            data = request.json
            PatientController.update_patient(id, data)
            return jsonify({'message': 'Paciente actualizado exitosamente'})
        
        elif request.method == 'DELETE':
            PatientController.delete_patient(id)
            return jsonify({'message': 'Paciente eliminado exitosamente'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@patient_bp.route('/api/pacientes/<int:id>/activar', methods=['POST'])
@login_required
def activate_patient(id):
    """Activar monitoreo para un paciente"""
    try:
        paciente = PatientController.activate_patient_monitoring(id)
        return jsonify({
            'message': f'Monitoreo activado para {paciente.nombre}',
            'paciente_id': paciente.id,
            'paciente_nombre': paciente.nombre
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
@patient_bp.route('/api/pacientes/<int:id>/notificaciones', methods=['GET'])
@login_required
def get_notifications(id):
    """Obtener notificaciones de un paciente"""
    try:
        from models import Notificacion
        notificaciones = Notificacion.query.filter_by(paciente_id=id).order_by(Notificacion.fecha_hora).all()
        return jsonify([{
            'id': n.id,
            'fecha_hora': n.fecha_hora.isoformat(),
            'enviado': n.enviado
        } for n in notificaciones])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@patient_bp.route('/api/pacientes/<int:id>/notificaciones', methods=['POST'])
@login_required
def schedule_notification(id):
    """Programar notificación de medicación"""
    try:
        data = request.json
        fecha_hora_str = data.get('fecha_hora')
        
        if not fecha_hora_str:
            return jsonify({'error': 'Fecha y hora son requeridas'}), 400
            
        # Parsear fecha y hora
        from datetime import datetime
        run_date = datetime.fromisoformat(fecha_hora_str)
        
        # Tópico y mensaje fijos para vibración
        topic = "healthmonitor/control"
        message = "VIBRAR"
        
        from scheduler_service import schedule_medication_reminder
        job_id = schedule_medication_reminder(run_date, topic, message)
        
        # Guardar en BD
        from models import db, Notificacion
        notificacion = Notificacion(
            paciente_id=id,
            fecha_hora=run_date,
            job_id=job_id
        )
        db.session.add(notificacion)
        db.session.commit()
        
        return jsonify({
            'message': 'Notificación programada exitosamente',
            'id': notificacion.id,
            'scheduled_for': run_date.isoformat()
        })
    except ValueError as e:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@patient_bp.route('/api/pacientes/<int:patient_id>/notificaciones/<int:id>', methods=['DELETE'])
@login_required
def delete_notification(patient_id, id):
    """Eliminar una notificación programada"""
    try:
        from models import db, Notificacion
        from scheduler_service import cancel_job
        
        notificacion = Notificacion.query.get_or_404(id)
        
        # Cancelar job si existe
        if notificacion.job_id:
            cancel_job(notificacion.job_id)
            
        db.session.delete(notificacion)
        db.session.commit()
        
        return jsonify({'message': 'Notificación eliminada exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
