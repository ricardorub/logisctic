from flask import Blueprint
from controller import predic_controller

predic_bp = Blueprint('predic', __name__)

# Rutas para la gestión de archivos
predic_bp.route('/file')(predic_controller.file_page_controller)
predic_bp.route('/upload', methods=['POST'])(predic_controller.upload_file_controller)
predic_bp.route('/delete_file/<filename>', methods=['DELETE'])(predic_controller.delete_file_controller)
predic_bp.route('/view_file/<filename>', endpoint='view_file')(predic_controller.view_file_controller)
predic_bp.route('/get_files')(predic_controller.get_files_controller)
predic_bp.route('/prediction', methods=['POST'])(predic_controller.prediction_controller)