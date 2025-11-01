from flask import Blueprint, render_template
from controller import test_compra_controller

test_compra_bp = Blueprint('test_compra', __name__)

@test_compra_bp.route('/test_compra')
def test_compra_page():
    return render_template('test_compra.html')

# Test Compra Routes
test_compra_bp.route('/api/test_compras', methods=['GET'])(test_compra_controller.get_all_test_compras)
test_compra_bp.route('/api/test_compras/import', methods=['POST'])(test_compra_controller.import_compras)
test_compra_bp.route('/api/test_compras', methods=['POST'])(test_compra_controller.create_test_compra)
test_compra_bp.route('/api/test_compras/<int:id>', methods=['PUT'])(test_compra_controller.update_test_compra)
test_compra_bp.route('/api/test_compras/<int:id>', methods=['DELETE'])(test_compra_controller.delete_test_compra)
test_compra_bp.route('/api/test_compras/details/<int:compra_id>', methods=['GET'])(test_compra_controller.get_test_compra_details)

# Test Inventario Routes
test_compra_bp.route('/api/test_inventario/import', methods=['POST'])(test_compra_controller.import_inventario)
test_compra_bp.route('/api/test_inventario', methods=['GET'])(test_compra_controller.get_all_test_inventario)
test_compra_bp.route('/api/test_inventario', methods=['POST'])(test_compra_controller.create_test_inventario)
test_compra_bp.route('/api/test_inventario/<string:nombre_producto>', methods=['PUT'])(test_compra_controller.update_test_inventario)
test_compra_bp.route('/api/test_inventario/<string:nombre_producto>', methods=['DELETE'])(test_compra_controller.delete_test_inventario)
test_compra_bp.route('/api/available_test_compra_ids', methods=['GET'])(test_compra_controller.get_available_test_compra_ids)

# Test Reposicion Routes
test_compra_bp.route('/api/test_reposiciones/import', methods=['POST'])(test_compra_controller.import_reposiciones)
test_compra_bp.route('/api/test_reposiciones', methods=['GET'])(test_compra_controller.get_all_test_reposiciones)
test_compra_bp.route('/api/test_reposiciones', methods=['POST'])(test_compra_controller.create_test_reposicion)
test_compra_bp.route('/api/test_reposiciones/<int:id>', methods=['PUT'])(test_compra_controller.update_test_reposicion)
test_compra_bp.route('/api/test_reposiciones/<int:id>', methods=['DELETE'])(test_compra_controller.delete_test_reposicion)
test_compra_bp.route('/api/test_productos_disponibles', methods=['GET'])(test_compra_controller.get_test_productos_disponibles)
