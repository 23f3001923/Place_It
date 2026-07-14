# backend/init_db.py
from flask import Flask
import os
from extensions import db
from models import User, CompanyProfile, StudentProfile, PlacementDrive, Application, Placement
from werkzeug.security import generate_password_hash

def create_app_and_db():
    app = Flask(__name__)
    # Pointing to a local SQLite file
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'instance', 'placement_portal.sqlite3')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        # 1. Create all tables
        db.create_all()
        print("Database tables created successfully.")

        # 2. Check if admin already exists
        admin_exists = User.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # 3. Create the pre-existing admin
            admin_user = User(
                email='admin@institute.edu',
                password_hash=generate_password_hash('admin123'), # Change this in production!
                role='admin',
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Pre-existing Admin created. Login: admin@institute.edu | Pass: admin123")
        else:
            print("Admin already exists. Skipping creation.")

if __name__ == '__main__':
    create_app_and_db()