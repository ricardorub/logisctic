from flask import Blueprint, render_template, request, jsonify
from controller.inventario_controller import (
    get_all_inventario_json,
    import_inventario_from_excel,
    export_inventario_to_excel,
    clear_all_inventario
)
import os

inventario_bp = Blueprint('inventario_bp', __name__, template_folder='templates')

@inventario_bp.route('/inventario')
def inventario_page():
    return render_template('inventario.html')

@inventario_bp.route('/api/inventario', methods=['GET'])
def get_inventario():
    return get_all_inventario_json()

@inventario_bp.route('/api/inventario/import', methods=['POST'])
def import_inventario():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.xlsx'):
        filepath = os.path.join('data', file.filename)
        file.save(filepath)
        import_inventario_from_excel(filepath)
        return jsonify({'success': 'File imported successfully'}), 200
    return jsonify({'error': 'Invalid file type'}), 400

@inventario_bp.route('/api/inventario/export', methods=['GET'])
def export_inventario():
    return export_inventario_to_excel()

@inventario_bp.route('/api/inventario/clear', methods=['POST'])
def clear_inventario():
    clear_all_inventario()
    return jsonify({'success': 'All data cleared'}), 200
