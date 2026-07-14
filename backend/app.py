# backend/app.py
import os
from flask import Flask
from extensions import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from celery_worker import make_celery

# Import blueprints
from routes.auth import auth_bp
from routes.company import company_bp
from routes.student import student_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    
    # Allow communication with the VueJS frontend
    app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Core Configurations
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'instance', 'placement_portal.sqlite3')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'placement-portal-super-secret-key-2026' # Change in production
    
    # Initialize Extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    return app

# 1. Create the global app instance
app = create_app()

# 2. Initialize Celery
celery = make_celery(app)

# 3. Bind the tasks to this celery instance
import tasks
tasks.celery = celery

tasks.generate_student_csv = celery.task(name='tasks.generate_student_csv')(tasks.generate_student_csv)
tasks.send_daily_reminders = celery.task(name='tasks.send_daily_reminders')(tasks.send_daily_reminders)
tasks.generate_monthly_report = celery.task(name='tasks.generate_monthly_report')(tasks.generate_monthly_report)

if __name__ == '__main__':
    # Run the Flask server
    app.run(debug=True, port=5000)