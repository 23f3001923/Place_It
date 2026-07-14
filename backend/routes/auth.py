# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from extensions import db
from models import User, StudentProfile, CompanyProfile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"message": "Account is deactivated or blacklisted."}), 403

    access_token = create_access_token(identity={'id': user.id, 'role': user.role})
    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "message": "Login successful"
    }), 200

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Email already registered"}), 400

    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    new_user = User(
        email=data.get('email'),
        password_hash=generate_password_hash(data.get('password')),
        role='student'
    )
    db.session.add(new_user)
    db.session.flush()

    new_profile = StudentProfile(
        user_id=new_user.id,
        full_name=data.get('full_name', ''),
        branch=data.get('branch', ''),
        cgpa=float(data.get('cgpa', 0.0)),
        passing_year=int(data.get('passing_year', 0)),
        resume_url=data.get('resume_url'),
        education=data.get('education'),
        skills=data.get('skills'),
        experience_years=float(data.get('experience_years')) if data.get('experience_years') else None,
        contact_number=data.get('contact_number')
    )
    db.session.add(new_profile)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Email already registered"}), 400

    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    new_user = User(
        email=data.get('email'),
        password_hash=generate_password_hash(data.get('password')),
        role='company'
    )
    db.session.add(new_user)
    db.session.flush()

    new_company = CompanyProfile(
        user_id=new_user.id,
        company_name=data.get('company_name', ''),
        hr_contact=data.get('hr_contact', ''),
        website=data.get('website', ''),
        industry=data.get('industry'),
        location=data.get('location'),
        phone=data.get('phone')
    )
    db.session.add(new_company)
    db.session.commit()

    return jsonify({"message": "Company registered. Pending admin approval."}), 201