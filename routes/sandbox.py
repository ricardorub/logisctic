from flask import Blueprint
from controller import sandbox_controller

sandbox_bp = Blueprint('sandbox', __name__)

sandbox_bp.route('/sandbox')(sandbox_controller.sandbox)
sandbox_bp.route('/sandbox/add', methods=['POST'])(sandbox_controller.add_item)
sandbox_bp.route('/sandbox/update/<int:item_id>', methods=['POST'])(sandbox_controller.update_item)
sandbox_bp.route('/sandbox/delete/<int:item_id>', methods=['POST'])(sandbox_controller.delete_item)
