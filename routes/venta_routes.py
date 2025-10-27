from flask import Blueprint, render_template
from controller import venta_controller

venta_bp = Blueprint('venta', __name__)

@venta_bp.route('/venta')
def venta_page():
    return render_template('venta.html')

@venta_bp.route('/api/ventas', methods=['GET'])
def get_all_ventas():
    return venta_controller.get_all_ventas()

@venta_bp.route('/api/ventas', methods=['POST'])
def create_venta():
    return venta_controller.create_venta()

@venta_bp.route('/api/ventas/<int:venta_id>', methods=['PUT'])
def update_venta(venta_id):
    return venta_controller.update_venta(venta_id)

@venta_bp.route('/api/ventas/<int:venta_id>', methods=['DELETE'])
def delete_venta(venta_id):
    return venta_controller.delete_venta(venta_id)
