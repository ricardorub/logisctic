from flask import Blueprint
from controller.laboratorio_controller import laboratorio_page

laboratorio_bp = Blueprint('laboratorio', __name__)

laboratorio_bp.route('/laboratorio')(laboratorio_page)
