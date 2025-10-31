from flask import Blueprint, render_template
from controller import reposicion_controller

reposicion_bp = Blueprint('reposicion', __name__)

@reposicion_bp.route('/reposicion')
def reposicion_page():
    return render_template('reposicion.html')

reposicion_bp.route('/api/reposiciones', methods=['GET'])(reposicion_controller.get_all_reposiciones)
reposicion_bp.route('/api/reposiciones', methods=['POST'])(reposicion_controller.create_reposicion)
reposicion_bp.route('/api/productos_disponibles', methods=['GET'])(reposicion_controller.get_productos_disponibles)
