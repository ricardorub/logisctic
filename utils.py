"""
Utilidades compartidas
"""
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorador para requerir inicio de sesión"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
