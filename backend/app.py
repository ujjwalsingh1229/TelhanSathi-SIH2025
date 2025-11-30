from flask import Flask, render_template, send_from_directory, url_for, redirect, session
from flask_cors import CORS
import os
from dotenv import load_dotenv

from extensions import db

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure session
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///telhan_sathi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize db with app
db.init_app(app)

# Import blueprints (after db is initialized)
from routes.auth import auth_bp
from routes.fayda_calculator import fayda_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(fayda_bp)

@app.route('/')
def home():
    """Root route - redirect to login if not authenticated, else to profile"""
    if 'farmer_id_verified' in session:
        return redirect(url_for('auth.profile'))
    return redirect(url_for('auth.login'))

@app.route('/index')
def index():
    """Redirect to login"""
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    """Simple dashboard placeholder. If you have a full dashboard blueprint, replace this."""
    # If user not logged in, send to login
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
