from flask import Blueprint
from controller import predic_controller

predic_bp = Blueprint('predic', __name__)

# Rutas para la gestión de archivos
predic_bp.route('/file')(predic_controller.file_page_controller)
predic_bp.route('/upload', methods=['POST'])(predic_controller.upload_file_controller)
predic_bp.route('/delete_file/<filename>', methods=['DELETE'])(predic_controller.delete_file_controller)
predic_bp.route('/view_file/<filename>')(predic_controller.view_file_controller)
predic_bp.route('/get_files')(predic_controller.get_files_controller)
predic_bp.route('/get_estado_counts/<filename>')(predic_controller.get_estado_counts_controller)

# Rutas para el Laboratorio de Optimización
predic_bp.route('/laboratorio')(predic_controller.laboratorio_page_controller)
predic_bp.route('/api/extract_critical', methods=['POST'])(predic_controller.extract_critical_data_controller)
predic_bp.route('/api/get_lab_data')(predic_controller.get_lab_data_controller)
predic_bp.route('/api/apply_deep_learning', methods=['POST'])(predic_controller.apply_deep_learning_controller)