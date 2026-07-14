# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy

# Initialize the database globally so it can be imported across the app
db = SQLAlchemy()