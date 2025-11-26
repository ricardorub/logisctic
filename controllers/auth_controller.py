"""
Controlador para la autenticación de usuarios
"""
from flask import session, flash
from models import Usuario
from werkzeug.security import check_password_hash

class AuthController:
    """Controlador para gestión de sesión y usuarios"""
    
    @staticmethod
    def login(email, password):
        """
        Intenta iniciar sesión con email y contraseña
        Retorna True si es exitoso, False si falla
        """
        user = Usuario.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.nombre
            session['user_role'] = user.rol
            return True
        
        return False
    
    @staticmethod
    def logout():
        """Cierra la sesión del usuario"""
        session.clear()
    
    @staticmethod
    def is_logged_in():
        """Verifica si hay un usuario logueado"""
        return 'user_id' in session
    
    @staticmethod
    def get_current_user():
        """Obtiene el usuario actual de la sesión"""
        if 'user_id' in session:
            return Usuario.query.get(session['user_id'])
        return None
