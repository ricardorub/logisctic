import os
from flask import Flask, redirect, url_for, session, render_template, request
from model.db import db
from routes.auth import auth_bp
from routes.predic import predic_bp
from routes.contact import contact_bp
from routes.compra_routes import compra_bp
from routes.inventario_routes import inventario_bp
from routes.venta_routes import venta_bp

app = Flask(__name__)

# --- Configurations ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/predic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- Directory Creation ---
# Ensure upload and data folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# --- Database Initialization ---
db.init_app(app)

# --- Blueprint Registration ---
app.register_blueprint(auth_bp)
app.register_blueprint(predic_bp) # Routes are defined from root in the blueprint
app.register_blueprint(contact_bp)
app.register_blueprint(compra_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(venta_bp)

# --- Core Routes ---

@app.route('/')
def index():
    """Render the main index page."""
    user = None
    if 'user_id' in session:
        user = {
            'email': session.get('user_email'),
            'first_name': session.get('user_first_name', ''),
            'last_name': session.get('user_last_name', '')
        }
    return render_template('index.html', user=user)

@app.route('/home')
def home():
    """Redirect to the file page if logged in, otherwise to index."""
    if 'user_id' in session:
        return redirect(url_for('file'))
    else:
        return redirect(url_for('index'))

# --- Utility and Test Routes ---

@app.route('/reset-db')
def reset_db():
    """Reset the database and create a test user."""
    try:
        from model.models import User, ChatSession, ChatMessage, Contact
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            test_user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            db.session.add(test_user)
            db.session.commit()
            
        return "Database has been reset and test user created."
    except Exception as e:
        return f"An error occurred while resetting the database: {e}"

@app.route('/test-contact')
def test_contact():
    """Render a test page for the contact form."""
    return """
    <h1>Prueba del Formulario de Contacto</h1>
    <form id="testForm">
        <input type="text" name="name" placeholder="Nombre" required><br>
        <input type="email" name="email" placeholder="Email" required><br>
        <input type="text" name="subject" placeholder="Asunto" required><br>
        <textarea name="message" placeholder="Mensaje" required></textarea><br>
        <button type="submit">Enviar</button>
    </form>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $('#testForm').submit(function(e) {
            e.preventDefault();
            const formData = $(this).serializeArray();
            const data = {};
            formData.forEach(item => { data[item.name] = item.value; });
            
            $.ajax({
                url: '/api/contact',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function(response) {
                    alert('Éxito: ' + response.message);
                },
                error: function(xhr) {
                    alert('Error: ' + (xhr.responseJSON?.error || 'Error desconocido'));
                }
            });
        });
    </script>
    """

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    return render_template('dashboard.html')

@app.route('/compra')
def compra():
    """Render the compra page."""
    return render_template('compra.html')

@app.route('/inventario')
def inventario():
    """Render the inventario page."""
    return render_template('inventario.html')

@app.route('/venta')
def venta():
    """Render the venta page."""
    return render_template('venta.html')

@app.route('/sandbox')
def sandbox():
    """Render the sandbox page."""
    return render_template('sandbox.html')

@app.route('/file')
def file():
    """Render the file page."""
    return render_template('file.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')