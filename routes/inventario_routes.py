from flask import Blueprint, render_template
from controller import inventario_controller

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/inventario')
def inventario_page():
    return render_template('inventario.html')

inventario_bp.route('/api/inventario', methods=['GET'])(inventario_controller.get_all_inventario)
inventario_bp.route('/api/inventario', methods=['POST'])(inventario_controller.create_inventario)
inventario_bp.route('/api/inventario/<int:item_id>', methods=['PUT'])(inventario_controller.update_inventario)
inventario_bp.route('/api/inventario/<int:item_id>', methods=['DELETE'])(inventario_controller.delete_inventario)

inventario_bp.route('/api/inventario/productos', methods=['GET'])(inventario_controller.get_productos_inventario)
