from flask import Flask, redirect, url_for
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1/predic'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from routes.inventario_routes import inventario_bp
    app.register_blueprint(inventario_bp)

    @app.route('/')
    def index():
        return redirect(url_for('inventario_bp.inventario_page'))

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
