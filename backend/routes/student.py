# backend/routes/student.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import PlacementDrive, Application, StudentProfile
import tasks

student_bp = Blueprint('student', __name__)

def is_student(identity):
    return identity.get('role') == 'student'

@student_bp.route('/drives/approved', methods=['GET'])
@jwt_required()
def get_approved_drives():
    if not is_student(get_jwt_identity()):
        return jsonify({"message": "Unauthorized"}), 403
    
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    result = [{"id": d.id, "company_name": d.company.company_name, "title": d.job_title, "cgpa_req": d.eligibility_cgpa, "deadline": d.application_deadline.strftime('%Y-%m-%d')} for d in drives]
    return jsonify(result), 200

@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@jwt_required()
def apply_to_drive(drive_id):
    identity = get_jwt_identity()
    if not is_student(identity):
        return jsonify({"message": "Unauthorized"}), 403

    student = StudentProfile.query.filter_by(user_id=identity['id']).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != 'Approved':
        return jsonify({"message": "Cannot apply to a drive that is not approved."}), 400

    if student.cgpa < drive.eligibility_cgpa:
        return jsonify({"message": f"Ineligible: Minimum CGPA {drive.eligibility_cgpa} required."}), 400

    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing_app:
        return jsonify({"message": "Already applied to this drive."}), 400

    app = Application(student_id=student.id, drive_id=drive_id)
    db.session.add(app)
    db.session.commit()
    return jsonify({"message": "Successfully applied."}), 201

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    identity = get_jwt_identity()
    if not is_student(identity):
        return jsonify({"message": "Unauthorized"}), 403

    student = StudentProfile.query.filter_by(user_id=identity['id']).first()
    apps = Application.query.filter_by(student_id=student.id).all()

    result = [{"app_id": a.id, "company_name": a.drive.company.company_name, "job_title": a.drive.job_title, "status": a.status, "applied_on": a.applied_on.strftime('%Y-%m-%d')} for a in apps]
    return jsonify(result), 200

@student_bp.route('/export-history', methods=['POST'])
@jwt_required()
def trigger_export():
    identity = get_jwt_identity()
    if not is_student(identity):
        return jsonify({"message": "Unauthorized"}), 403

    student = StudentProfile.query.filter_by(user_id=identity['id']).first()
    task = tasks.generate_student_csv.delay(student.id)
    return jsonify({"message": "Export started! CSV will be saved to your backend folder.", "task_id": task.id}), 202

# --- NEW: PROFILE MANAGEMENT ROUTES ---
@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    if not is_student(identity):
        return jsonify({"message": "Unauthorized"}), 403
    
    student = StudentProfile.query.filter_by(user_id=identity['id']).first()
    return jsonify({
        "cgpa": student.cgpa, 
        "passing_year": student.passing_year, 
        "resume_url": student.resume_url or ""
    }), 200

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    if not is_student(identity):
        return jsonify({"message": "Unauthorized"}), 403

    student = StudentProfile.query.filter_by(user_id=identity['id']).first()
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400

    if 'cgpa' in data:
        student.cgpa = float(data['cgpa'])
    if 'resume_url' in data:
        student.resume_url = data['resume_url']
    if 'passing_year' in data:
        student.passing_year = int(data['passing_year'])

    db.session.commit()
    return jsonify({"message": "Profile updated successfully."}), 200