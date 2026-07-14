# backend/routes/company.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import PlacementDrive, CompanyProfile, Application, StudentProfile
from datetime import datetime

company_bp = Blueprint('company', __name__)

# Helper to check role
def is_company(identity):
    return identity.get('role') == 'company'

@company_bp.route('/drives', methods=['POST'])
@jwt_required()
def create_drive():
    identity = get_jwt_identity()
    if not is_company(identity):
        return jsonify({"message": "Unauthorized"}), 403

    company = CompanyProfile.query.filter_by(user_id=identity['id']).first()
    
    if company.approval_status != 'Approved':
        return jsonify({"message": "Company not yet approved by Admin."}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400
    try:
        deadline = datetime.strptime(data.get('application_deadline', ''), '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    if not data.get('job_title') or not data.get('job_description'):
        return jsonify({"message": "Job title and description are required."}), 400

    new_drive = PlacementDrive(
        company_id=company.id,
        job_title=data.get('job_title'),
        job_description=data.get('job_description'),
        eligibility_branch=data.get('eligibility_branch'),
        eligibility_cgpa=float(data.get('eligibility_cgpa', 0.0)),
        application_deadline=deadline,
        salary=data.get('salary'),
        skills_required=data.get('skills_required'),
        experience_required=data.get('experience_required'),
        benefits=data.get('benefits'),
        location=data.get('location')
    )
    db.session.add(new_drive)
    db.session.commit()

    return jsonify({"message": "Placement drive created. Pending admin approval."}), 201

@company_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_company_drives():
    identity = get_jwt_identity()
    if not is_company(identity):
        return jsonify({"message": "Unauthorized"}), 403

    company = CompanyProfile.query.filter_by(user_id=identity['id']).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    
    result = []
    for d in drives:
        # Count applicants
        app_count = Application.query.filter_by(drive_id=d.id).count()
        result.append({
            "id": d.id, 
            "title": d.job_title, 
            "status": d.status, 
            "deadline": d.application_deadline.strftime('%Y-%m-%d'), 
            "applicants": app_count
        })
    return jsonify(result), 200

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    identity = get_jwt_identity()
    if not is_company(identity):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400
    new_status = data.get('status')
    if not new_status:
        return jsonify({"message": "Status is required."}), 400

    company = CompanyProfile.query.filter_by(user_id=identity['id']).first()
    application = Application.query.get_or_404(app_id)

    if application.drive.company_id != company.id:
        return jsonify({"message": "Cannot update applications for another company."}), 403

    application.status = new_status
    db.session.commit()

    return jsonify({"message": f"Application status updated to {new_status}"}), 200

@company_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_company_applications():
    identity = get_jwt_identity()
    if not is_company(identity):
        return jsonify({"message": "Unauthorized"}), 403

    company = CompanyProfile.query.filter_by(user_id=identity['id']).first()
    
    # Get all drives for this company
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    drive_ids = [d.id for d in drives]
    
    # Get all applications mapped to those drives
    apps = Application.query.filter(Application.drive_id.in_(drive_ids)).all()
    
    result = [
        {
            "id": a.id, 
            "student_name": a.student.full_name, 
            "student_branch": a.student.branch,
            "student_cgpa": a.student.cgpa,
            "drive_title": a.drive.job_title, 
            "status": a.status
        } for a in apps
    ]
    return jsonify(result), 200