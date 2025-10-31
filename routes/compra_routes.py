from flask import Blueprint, render_template
from controller import compra_controller

compra_bp = Blueprint('compra', __name__)

@compra_bp.route('/compra')
def compra_page():
    return render_template('compra.html')

compra_bp.route('/api/compras', methods=['GET'])(compra_controller.get_all_compras)
compra_bp.route('/api/compras', methods=['POST'])(compra_controller.create_compra)
compra_bp.route('/api/compras/<int:compra_id>', methods=['PUT'])(compra_controller.update_compra)
compra_bp.route('/api/compras/<int:compra_id>', methods=['DELETE'])(compra_controller.delete_compra)

compra_bp.route('/api/productos', methods=['GET'])(compra_controller.get_productos)
compra_bp.route('/api/cantidad_total/<nombre_producto>', methods=['GET'])(compra_controller.get_cantidad_total)
compra_bp.route('/api/compra_ids', methods=['GET'])(compra_controller.get_all_compra_ids)
compra_bp.route('/api/compras/details/<int:compra_id>', methods=['GET'])(compra_controller.get_compra_details)
compra_bp.route('/api/available_compra_ids', methods=['GET'])(compra_controller.get_available_compra_ids)
