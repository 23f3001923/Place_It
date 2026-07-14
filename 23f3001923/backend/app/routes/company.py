from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from app.models import db, CompanyProfile, PlacementDrive, Application, StudentProfile
from app.utils import company_required

company_bp = Blueprint('company', __name__)

# Helper to resolve the authenticated company profile
def get_current_company():
    user_id = get_jwt_identity()
    return CompanyProfile.query.filter_by(user_id=int(user_id)).first()


# 1. Company Dashboard Metrics
@company_bp.route('/dashboard/stats', methods=['GET'])
@company_required()
def get_company_stats():
    company = get_current_company()
    
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    drive_ids = [d.id for d in drives]
    
    total_drives = len(drives)
    total_applicants = Application.query.filter(Application.drive_id.in_(drive_ids)).count() if drive_ids else 0
    total_shortlisted = Application.query.filter(Application.drive_id.in_(drive_ids), Application.status == 'Shortlisted').count() if drive_ids else 0

    return jsonify({
        "company_name": company.company_name,
        "approval_status": company.status,
        "total_posted_drives": total_drives,
        "total_received_applications": total_applicants,
        "total_shortlisted_candidates": total_shortlisted
    }), 200


# 2. Create a New Placement Drive (Awaits Admin Approval)
@company_bp.route('/drives', methods=['POST'])
@company_required()
def create_placement_drive():
    company = get_current_company()
    data = request.get_json()

    required_fields = ['job_title', 'job_description', 'eligibility_year', 'salary', 'application_deadline']
    if not all(k in data for k in required_fields):
        return jsonify({"message": "Missing required job structural configuration fields."}), 400

    try:
        deadline = datetime.strptime(data['application_deadline'], "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DDTHH:MM"}), 400

    new_drive = PlacementDrive(
        company_id=company.id,
        job_title=data['job_title'],
        job_description=data['job_description'],
        eligibility_branch=data.get('eligibility_branch', 'All'),
        eligibility_cgpa=float(data.get('eligibility_cgpa', 0.0)),
        eligibility_year=int(data['eligibility_year']),
        salary=float(data['salary']),
        application_deadline=deadline,
        status='Pending' # Default state requires explicit Admin confirmation
    )

    db.session.add(new_drive)
    db.session.commit()
    return jsonify({"message": "Placement drive created successfully. Awaiting Admin validation."}), 201

@company_bp.route('/drives/<int:drive_id>', methods=['PUT', 'DELETE'])
@company_required()
def manage_drive_actions(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    if request.method == 'DELETE':
        db.session.delete(drive)
        db.session.commit()
        return jsonify({"message": "Drive removed successfully"}), 200

    if request.method == 'PUT':
        data = request.get_json()
        drive.job_title = data.get('job_title', drive.job_title)
        drive.salary = data.get('salary', drive.salary)
        drive.job_description = data.get('job_description', drive.job_description)
        db.session.commit()
        return jsonify({"message": "Drive updated successfully"}), 200

# 3. View All Placement Drives Posted by Company
@company_bp.route('/drives', methods=['GET'])
@company_required()
def list_company_drives():
    company = get_current_company()
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    
    return jsonify([{
        "id": d.id,
        "job_title": d.job_title,
        "eligibility_cgpa": d.eligibility_cgpa,
        "salary": d.salary,
        "deadline": d.application_deadline.isoformat(),
        "status": d.status
    } for d in drives]), 200


# 4. Modify Job Drive Lifecycle Status (Active / Closed)
@company_bp.route('/drives/<int:drive_id>/lifecycle', methods=['PATCH'])
@company_required()
def toggle_drive_lifecycle(drive_id):
    company = get_current_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    
    data = request.get_json()
    new_status = data.get('status') # Expects: 'Approved' (Active) or 'Closed'
    
    if new_status not in ['Approved', 'Closed']:
        return jsonify({"message": "Companies can only transition state to Active (Approved) or Closed"}), 400

    if drive.status == 'Pending':
        return jsonify({"message": "Cannot modify lifecycle of a drive pending Admin verification."}), 403

    drive.status = new_status
    db.session.commit()
    return jsonify({"message": f"Placement drive status updated to {new_status}."}), 200


# 5. Get Applicants for a Specific Placement Drive
@company_bp.route('/drives/<int:drive_id>/applicants', methods=['GET'])
@company_required()
def view_drive_applicants(drive_id):
    company = get_current_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    applications = Application.query.filter_by(drive_id=drive.id).all()
    
    results = []
    for app in applications:
        student = StudentProfile.query.get(app.student_id)
        results.append({
            "application_id": app.id,
            "student_name": student.full_name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "skills": student.skills,
            "application_date": app.application_date.isoformat(),
            "status": app.status,
            "feedback": app.feedback
        })
        
    return jsonify(results), 200


# 6. Process Application Review Status & Schedule Interviews
@company_bp.route('/applications/<int:app_id>/review', methods=['PATCH'])
@company_required()
def review_applicant(app_id):
    company = get_current_company()
    
    # Query validation matrix to verify ownership context
    application = Application.query.join(PlacementDrive).filter(
        Application.id == app_id, 
        PlacementDrive.company_id == company.id
    ).first_or_404()
    
    data = request.get_json()
    new_status = data.get('status') # Expects: 'Shortlisted', 'Selected', 'Rejected'
    feedback = data.get('feedback', '')

    if new_status not in ['Shortlisted', 'Selected', 'Rejected']:
        return jsonify({"message": "Invalid review status state assignment."}), 400

    application.status = new_status
    
    # Append feedback or interview coordination parameters directly into context tracking
    if new_status == 'Shortlisted' and 'interview_time' in data:
        application.feedback = f"Interview Scheduled: {data['interview_time']}. {feedback}"
    else:
        application.feedback = feedback

    db.session.commit()
    return jsonify({"message": f"Applicant record successfully marked as {new_status}."}), 200