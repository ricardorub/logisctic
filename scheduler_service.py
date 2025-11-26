from apscheduler.schedulers.background import BackgroundScheduler
from mqtt_service import publish_message
from datetime import datetime

scheduler = BackgroundScheduler()

def init_scheduler(app):
    """Inicializa el planificador de tareas"""
    if not scheduler.running:
        scheduler.start()
    
    # Tarea de limpieza de datos antiguos (movida desde app.py)
    # Necesitamos importar db y SensorData aquí o pasarlos, pero para evitar importaciones circulares
    # podemos definir la función de limpieza dentro de init_scheduler o usar app context
    
    from models import db, SensorData
    from datetime import timedelta

    def clean_old_data():
        with app.app_context():
            days = app.config.get('OLD_DATA_RETENTION_DAYS', 30)
            old_records = SensorData.query.filter(
                SensorData.fecha < datetime.now() - timedelta(days=days)
            ).delete()
            db.session.commit()
            print(f"Deleted {old_records} old records")

    scheduler.add_job(func=clean_old_data, trigger="interval", hours=24, id='clean_old_data', replace_existing=True)

def schedule_medication_reminder(run_date, topic, message):
    """Programa un recordatorio de medicación (solo vibración)"""
    
    def job_function(topic, message):
        # Enviar comando de vibración
        if topic and message:
            publish_message(topic, message)

    job = scheduler.add_job(
        func=job_function,
        trigger='date',
        run_date=run_date,
        args=[topic, message]
    )
    return job.id

def cancel_job(job_id):
    """Cancela un trabajo programado"""
    try:
        scheduler.remove_job(job_id)
        return True
    except Exception as e:
        print(f"Error cancelling job {job_id}: {e}")
        return False
