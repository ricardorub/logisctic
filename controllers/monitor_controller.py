"""
Controlador para el monitoreo en tiempo real
"""
from models import db, Paciente, SensorData
from datetime import datetime, timedelta

class MonitorController:
    """Controlador para operaciones de monitoreo en tiempo real"""
    
    @staticmethod
    def get_active_patient():
        """Obtiene el paciente activo para monitoreo"""
        return Paciente.query.filter_by(activo=True).first()
    
    @staticmethod
    def get_all_active_patients():
        """Obtiene todos los pacientes activos para el selector"""
        return Paciente.query.filter_by(activo=True).all()
    
    @staticmethod
    def get_sensor_data(time_range='5min', patient_id=None):
        """
        Obtiene datos de sensores para un rango de tiempo específico
        
        Args:
            time_range: Rango de tiempo ('5min', '15min', '30min', 'all')
            patient_id: ID del paciente (opcional, usa el activo por defecto)
        """
        now = datetime.now()
        
        # Determinar el límite de tiempo
        if time_range == '5min':
            time_limit = now - timedelta(minutes=5)
        elif time_range == '15min':
            time_limit = now - timedelta(minutes=15)
        elif time_range == '30min':
            time_limit = now - timedelta(minutes=30)
        else:
            time_limit = None
        
        # Construir query
        query = SensorData.query
        
        # Filtrar por paciente
        if patient_id:
            query = query.filter(SensorData.paciente_id == int(patient_id))
        else:
            # Usar el paciente activo por defecto
            paciente_activo = MonitorController.get_active_patient()
            if paciente_activo:
                query = query.filter(SensorData.paciente_id == paciente_activo.id)
        
        # Filtrar por tiempo
        if time_limit:
            query = query.filter(SensorData.fecha >= time_limit)
        
        records = query.order_by(SensorData.fecha.asc()).all()
        
        return records
    
    @staticmethod
    def format_sensor_data(records, current_readings):
        """
        Formatea los datos de sensores para la respuesta API
        
        Args:
            records: Lista de registros de SensorData
            current_readings: Lecturas actuales del MQTT
        """
        now = datetime.now()
        
        # Preparar datos históricos
        history_temp = [{'x': r.fecha.strftime("%H:%M:%S"), 'y': float(r.valor)} for r in records]
        history_hr = [{'x': r.fecha.strftime("%H:%M:%S"), 'y': int(r.heart_rate)} for r in records]
        history_spo2 = [{'x': r.fecha.strftime("%H:%M:%S"), 'y': int(r.spo2)} for r in records]
        
        # Determinar valores actuales
        if current_readings['last_update'] and (now - current_readings['last_update']).seconds < 30:
            temp_value = current_readings['temperature']
            hr_value = current_readings['heart_rate']
            spo2_value = current_readings['spo2']
        elif records:
            last_record = records[-1]
            temp_value = float(last_record.valor)
            hr_value = int(last_record.heart_rate)
            spo2_value = int(last_record.spo2)
        else:
            temp_value = None
            hr_value = None
            spo2_value = None
        
        return {
            'temperatura_actual': temp_value,
            'heart_rate': hr_value,
            'spo2': spo2_value,
            'historico_temperatura': history_temp,
            'historico_heart': history_hr,
            'historico_spo2': history_spo2,
            'last_update': current_readings['last_update'].isoformat() if current_readings['last_update'] else None
        }
    
    @staticmethod
    def get_stats_data(days=7, patient_id=None):
        """Obtiene datos estadísticos para un número de días (para un paciente individual o general)"""
        now = datetime.now()
        time_limit = now - timedelta(days=days)
        
        query = SensorData.query.filter(SensorData.fecha >= time_limit)
        
        if patient_id:
            query = query.filter(SensorData.paciente_id == int(patient_id))
        else:
            # Si no se especifica paciente, usamos el activo por defecto para stats también
            # o podríamos mostrar global, pero para "Panel de Salud" suele ser individual
            paciente_activo = MonitorController.get_active_patient()
            if paciente_activo:
                query = query.filter(SensorData.paciente_id == paciente_activo.id)
            
        records = query.order_by(SensorData.fecha.asc()).all()
        
        # Preparar datos
        dias = [r.fecha.isoformat() for r in records]
        temperatura = [float(r.valor) for r in records]
        heart_rate = [int(r.heart_rate) for r in records]
        spo2 = [int(r.spo2) for r in records]
        
        # Predicciones LSTM (simuladas por ahora)
        predictions = []
        if temperatura:
            last_temp = temperatura[-1]
            predictions = [last_temp + i * 0.1 for i in range(1, 4)]
        
        return {
            'dias': dias,
            'temperatura': temperatura,
            'heart_rate': heart_rate,
            'spo2': spo2,
            'predictions': predictions,
            'last_prediction_update': datetime.now().isoformat()
        }

    @staticmethod
    def get_global_stats():
        """Obtiene estadísticas globales de todos los pacientes"""
        # Estadísticas de pacientes
        total_pacientes = Paciente.query.count()
        normales = Paciente.query.filter_by(estado='normal').count()
        advertencia = Paciente.query.filter_by(estado='advertencia').count()
        peligro = Paciente.query.filter(Paciente.estado.in_(['peligro', 'critico'])).count()
        
        # Pacientes que requieren atención
        pacientes_criticos = Paciente.query.filter(
            Paciente.estado.in_(['advertencia', 'peligro', 'critico'])
        ).all()
        
        # Promedios de sensores (últimas 24h)
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        avg_temp = db.session.query(db.func.avg(SensorData.valor)).filter(
            SensorData.fecha >= last_24h
        ).scalar() or 0
        
        avg_hr = db.session.query(db.func.avg(SensorData.heart_rate)).filter(
            SensorData.fecha >= last_24h
        ).scalar() or 0
        
        avg_spo2 = db.session.query(db.func.avg(SensorData.spo2)).filter(
            SensorData.fecha >= last_24h
        ).scalar() or 0
        
        return {
            'total_pacientes': total_pacientes,
            'estados': {
                'normal': normales,
                'advertencia': advertencia,
                'peligro': peligro
            },
            'promedios_24h': {
                'temperatura': round(avg_temp, 1),
                'heart_rate': int(avg_hr),
                'spo2': int(avg_spo2)
            },
            'pacientes_criticos': [
                {
                    'id': p.id,
                    'nombre': p.nombre,
                    'estado': p.estado,
                    'foto': p.foto_url
                } for p in pacientes_criticos
            ]
        }
