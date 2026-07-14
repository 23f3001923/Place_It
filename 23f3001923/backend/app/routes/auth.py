from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User, StudentProfile, CompanyProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    
    # Simple validation
    required_fields = ['email', 'password', 'full_name', 'contact_number', 'branch', 'cgpa', 'graduation_year']
    if not all(k in data for k in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400

    # Create base user record
    hashed_pw = generate_password_hash(data['password'], method='scrypt')
    new_user = User(email=data['email'], password_hash=hashed_pw, role='Student', is_active=True)
    
    db.session.add(new_user)
    db.session.flush()  # Extract user ID before commit

    # Create associated student profile
    student_profile = StudentProfile(
        user_id=new_user.id,
        full_name=data['full_name'],
        contact_number=data['contact_number'],
        branch=data['branch'],
        cgpa=float(data['cgpa']),
        graduation_year=int(data['graduation_year']),
        skills=data.get('skills', '')
    )
    
    db.session.add(student_profile)
    db.session.commit()
    
    return jsonify({"message": "Student registered successfully"}), 201


@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()
    
    required_fields = ['email', 'password', 'company_name', 'hr_contact', 'website', 'industry', 'location']
    if not all(k in data for k in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400

    hashed_pw = generate_password_hash(data['password'], method='scrypt')
    # Companies default to active user but their profile status determines system access
    new_user = User(email=data['email'], password_hash=hashed_pw, role='Company', is_active=True)
    
    db.session.add(new_user)
    db.session.flush()

    # Create company profile with "Pending" admin approval status
    company_profile = CompanyProfile(
        user_id=new_user.id,
        company_name=data['company_name'],
        hr_contact=data['hr_contact'],
        website=data['website'],
        industry=data['industry'],
        location=data['location'],
        status='Pending'
    )
    
    db.session.add(company_profile)
    db.session.commit()
    
    return jsonify({"message": "Company registered successfully. Awaiting Admin approval."}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"message": "Your account has been deactivated/blacklisted by Admin."}), 403

    # Extra structural guard check for Company Approvals
    if user.role == 'Company':
        profile = CompanyProfile.query.filter_by(user_id=user.id).first()
        if profile.status == 'Pending':
            return jsonify({"message": "Your company profile is pending Admin approval."}), 403
        elif profile.status == 'Blacklisted':
            return jsonify({"message": "Your company access has been blacklisted."}), 403

    # Generate JWT containing user metadata
    additional_claims = {"role": user.role}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    
    return jsonify({
        "token": access_token,
        "role": user.role,
        "message": "Login successful"
    }), 200