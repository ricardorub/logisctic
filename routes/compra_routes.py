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
