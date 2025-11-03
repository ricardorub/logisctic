from flask import Flask
from routes.inventario_routes import inventario_bp
from routes.auth import auth_bp
from routes.contact import contact_bp
from routes.home import home_bp
from model.models import db
import os

def create_app():
    app = Flask(__name__)

    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1/predic'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)