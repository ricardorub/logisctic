"""
Rutas para autenticación
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if AuthController.is_logged_in():
        return redirect(url_for('monitor.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if AuthController.login(email, password):
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('monitor.index'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    AuthController.logout()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))
