from flask import Blueprint, render_template
from controller import inventario_controller

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/inventario')
def inventario_page():
    return render_template('inventario.html')

@inventario_bp.route('/api/inventario', methods=['GET'])
def get_all_inventario():
    return inventario_controller.get_all_inventario()

@inventario_bp.route('/api/inventario', methods=['POST'])
def create_inventario():
    return inventario_controller.create_inventario()

@inventario_bp.route('/api/inventario/<int:item_id>', methods=['PUT'])
def update_inventario(item_id):
    return inventario_controller.update_inventario(item_id)

@inventario_bp.route('/api/inventario/<int:item_id>', methods=['DELETE'])
def delete_inventario(item_id):
    return inventario_controller.delete_inventario(item_id)

@inventario_bp.route('/api/inventario/productos', methods=['GET'])
def get_productos_inventario():
    return inventario_controller.get_productos_inventario()
