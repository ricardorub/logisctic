from flask import Blueprint, render_template

sandbox_bp = Blueprint('sandbox', __name__)

@sandbox_bp.route('/sandbox')
def sandbox_page():
    return render_template('sandbox.html')
