from flask import Blueprint
from controller import crud_controller

crud_bp = Blueprint('crud', __name__)

crud_bp.route('/crud', methods=['GET'])(crud_controller.get_items)
crud_bp.route('/crud/add', methods=['POST'])(crud_controller.add_item)
crud_bp.route('/crud/update/<int:item_id>', methods=['POST'])(crud_controller.update_item)
crud_bp.route('/crud/delete/<int:item_id>', methods=['POST'])(crud_controller.delete_item)
crud_bp.route('/crud/export', methods=['GET'])(crud_controller.export_excel)
