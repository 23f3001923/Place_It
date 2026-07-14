from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import db, StudentProfile, PlacementDrive, Application, CompanyProfile, User
from app.utils import student_required
from app.tasks import export_student_applications_csv

student_bp = Blueprint('student', __name__)

def get_current_student():
    """Helper utility to resolve the student profile based on JWT authentication identity."""
    user_id = get_jwt_identity()
    return StudentProfile.query.filter_by(user_id=int(user_id)).first()


# =========================================================
# 1. Profile Management Endpoints
# =========================================================
@student_bp.route('/profile', methods=['GET', 'PUT'])
@student_required()
def manage_profile():
    student = get_current_student()
    if not student:
        return jsonify({"message": "Student profile not found."}), 404
    
    if request.method == 'GET':
        return jsonify({
            "full_name": student.full_name,
            "contact_number": student.contact_number,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "graduation_year": student.graduation_year,
            "skills": student.skills,
            "resume_path": student.resume_path
        }), 200

    # PUT request processing block
    data = request.get_json() or {}
    student.full_name = data.get('full_name', student.full_name)
    student.contact_number = data.get('contact_number', student.contact_number)
    student.skills = data.get('skills', student.skills)
    student.resume_path = data.get('resume_path', student.resume_path)
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully."}), 200


# =========================================================
# 2. Drive Search and Eligibility Discovery Engine
# =========================================================

@student_bp.route('/drives', methods=['GET'])
@student_required()
def list_available_drives():
    student = get_current_student()
    
    # Restrict visibility globally to Approved open listings
    query = PlacementDrive.query.filter_by(status='Approved')
    
    search_company = request.args.get('company', '')
    search_position = request.args.get('position', '')
    
    if search_company:
        query = query.join(CompanyProfile).filter(CompanyProfile.company_name.like(f"%{search_company}%"))
    if search_position:
        query = query.filter(PlacementDrive.job_title.like(f"%{search_position}%"))
        
    drives = query.all()
    results = []
    
    for d in drives:
        # Dynamic calculations comparing student qualifications with explicit constraints
        is_eligible = (
            student.cgpa >= d.eligibility_cgpa and 
            student.graduation_year == d.eligibility_year and
            (d.eligibility_branch == 'All' or student.branch in d.eligibility_branch)
        )
        
        # Cross-reference existing entries to flag previous application status
        already_applied = Application.query.filter_by(student_id=student.id, drive_id=d.id).first() is not None
        
        results.append({
            "drive_id": d.id,
            "company_name": d.company.company_name,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "salary": d.salary,
            "deadline": d.application_deadline.isoformat(),
            "is_eligible": is_eligible,
            "already_applied": already_applied
        })
        
    return jsonify(results), 200


# =========================================================
# 3. Job Application Handler (With Eligibility Enforcement)
# =========================================================
@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@student_required()
def apply_to_drive(drive_id):
    student = get_current_student()
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    if drive.status != 'Approved':
        return jsonify({"message": "Applications are closed or not approved for this drive."}), 400

    # Guard Check: Prevent multiple submissions (Milestone 6)
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing_app:
        return jsonify({"message": "Duplicate submission detected. You have already applied to this drive."}), 400

    # Strict Criteria Check Validation Steps
    if student.cgpa < drive.eligibility_cgpa:
        return jsonify({"message": "Application rejected: Minimum CGPA criteria not met."}), 403
    if student.graduation_year != drive.eligibility_year:
        return jsonify({"message": "Application rejected: Graduation batch mismatch."}), 403
    if drive.eligibility_branch != 'All' and student.branch not in drive.eligibility_branch:
        return jsonify({"message": "Application rejected: Branch eligibility mismatch."}), 403

    # Generate explicit fresh history record row
    new_application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status='Applied'
    )
    
    db.session.add(new_application)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully."}), 201


# =========================================================
# 4. Status Tracking Pipeline (Milestone 6 Completion)
# =========================================================
@student_bp.route('/applications', methods=['GET'])
@student_required()
def application_history():
    student = get_current_student()
    applications = Application.query.filter_by(student_id=student.id).all()
    
    return jsonify([{
        "application_id": app.id,
        "company_name": app.drive.company.company_name,
        "job_title": app.drive.job_title,
        "application_date": app.application_date.isoformat(),
        "status": app.status,
        "feedback": app.feedback
    } for app in applications]), 200


# =========================================================
# 5. Milestone 7: Async CSV Placement Export Process Request
# =========================================================
@student_bp.route('/export-applications', methods=['POST'])
@student_required()
def trigger_csv_export():
    student = get_current_student()
    user = User.query.get(student.user_id)
    
    if not user:
        return jsonify({"message": "User association error encountered."}), 404

    # Offload the transaction operation payload safely onto the Celery daemon infrastructure
    export_student_applications_csv.delay(student.id, user.email)
    
    return jsonify({
        "message": "Export job started successfully. You will be notified when your CSV is ready."
    }), 202