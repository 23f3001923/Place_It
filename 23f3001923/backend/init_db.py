import os
import sys

# Crucial Path Fix: Add the backend root folder to the Python path 
# so modules like 'tasks' can be imported seamlessly from anywhere.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from werkzeug.security import generate_password_hash
from app import db, create_app
from app.models import User

def initialize_database():
    app = create_app()
    with app.app_context():
        # Build the SQLite tables programmatically
        db.create_all()
        print("Database tables initialized successfully.")

        # Pre-seed Admin User
        admin_email = "admin@institute.edu"
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                password_hash=generate_password_hash("AdminRootPassword2026", method='scrypt'),
                role="Admin",
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin account created successfully! Login: {admin_email}")
        else:
            print("Admin account already exists.")

if __name__ == '__main__':
    initialize_database()