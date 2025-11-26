"""
Controlador para la gestión de pacientes
"""
from models import db, Paciente
from datetime import datetime

class PatientController:
    """Controlador para operaciones CRUD de pacientes"""
    
    @staticmethod
    def get_all_patients():
        """Obtiene todos los pacientes del sistema"""
        # Devolvemos todos para que no desaparezcan al activar el monitoreo de uno
        return Paciente.query.all()
    
    @staticmethod
    def get_patient_by_id(patient_id):
        """Obtiene un paciente por su ID"""
        return Paciente.query.get_or_404(patient_id)
    
    @staticmethod
    def create_patient(data):
        """Crea un nuevo paciente"""
        nuevo_paciente = Paciente(
            nombre=data.get('nombre'),
            edad=data.get('edad'),
            email=data.get('email'),
            telefono=data.get('telefono'),
            device_id=data.get('device_id'),
            estado=data.get('estado', 'normal'),
            foto_url=data.get('foto_url'),
            notas=data.get('notas')
        )
        db.session.add(nuevo_paciente)
        db.session.commit()
        return nuevo_paciente
    
    @staticmethod
    def update_patient(patient_id, data):
        """Actualiza un paciente existente"""
        paciente = Paciente.query.get_or_404(patient_id)
        
        paciente.nombre = data.get('nombre', paciente.nombre)
        paciente.edad = data.get('edad', paciente.edad)
        paciente.email = data.get('email', paciente.email)
        paciente.telefono = data.get('telefono', paciente.telefono)
        paciente.device_id = data.get('device_id', paciente.device_id)
        paciente.estado = data.get('estado', paciente.estado)
        paciente.foto_url = data.get('foto_url', paciente.foto_url)
        paciente.notas = data.get('notas', paciente.notas)
        
        db.session.commit()
        return paciente
    
    @staticmethod
    def delete_patient(patient_id):
        """Elimina (desactiva) un paciente"""
        paciente = Paciente.query.get_or_404(patient_id)
        paciente.activo = False
        db.session.commit()
        return paciente
    
    @staticmethod
    def activate_patient_monitoring(patient_id):
        """Activa el monitoreo para un paciente específico"""
        # Desactivar todos los pacientes
        Paciente.query.update({Paciente.activo: False})
        
        # Activar el paciente seleccionado
        paciente = Paciente.query.get_or_404(patient_id)
        paciente.activo = True
        db.session.commit()
        
        return paciente
    
    @staticmethod
    def get_patients_stats():
        """Obtiene estadísticas de pacientes"""
        pacientes = Paciente.query.filter_by(activo=True).all()
        
        return {
            'total': len(pacientes),
            'normales': len([p for p in pacientes if p.estado == 'normal']),
            'advertencia': len([p for p in pacientes if p.estado == 'advertencia']),
            'criticos': len([p for p in pacientes if p.estado == 'critico'])
        }
