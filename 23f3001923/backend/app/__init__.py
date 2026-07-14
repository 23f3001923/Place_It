from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from app.models import db
from config import Config

cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # backend/app/__init__.py
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    # Ensure methods are allowed
    app.config['CORS_METHODS'] = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    app.config['CORS_HEADERS'] = ["Content-Type", "Authorization"]

    db.init_app(app)
    jwt = JWTManager(app)
    cache.init_app(app)

    from app.routes import auth_bp, admin_bp, company_bp, student_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    return app

