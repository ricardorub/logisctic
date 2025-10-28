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

@inventario_bp.route('/api/inventario/<string:nombre_producto>', methods=['PUT'])
def update_inventario(nombre_producto):
    return inventario_controller.update_inventario(nombre_producto)

@inventario_bp.route('/api/inventario/<string:nombre_producto>', methods=['DELETE'])
def delete_inventario(nombre_producto):
    return inventario_controller.delete_inventario(nombre_producto)

@inventario_bp.route('/api/inventario/productos', methods=['GET'])
def get_productos_inventario():
    return inventario_controller.get_productos_inventario()

@inventario_bp.route('/api/inventario/cantidad_total/<nombre_producto>', methods=['GET'])
def get_cantidad_total_inventario(nombre_producto):
    return inventario_controller.get_cantidad_total_inventario(nombre_producto)

@inventario_bp.route('/api/inventario/export', methods=['GET'])
def export_inventario():
    return inventario_controller.export_inventario()
