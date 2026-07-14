from flask import Blueprint, request, jsonify
from app.models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
from app.utils import admin_required
import traceback

admin_bp = Blueprint('admin', __name__)

# 1. Admin Dashboard Aggregate Metrics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required()
def get_dashboard_stats():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_placement_drives": total_drives,
        "total_applications": total_applications
    }), 200


# 2. Company Registration Management (Approve / Reject)
@admin_bp.route('/companies/<int:company_id>/status', methods=['PATCH'])
@admin_required()
def update_company_status(company_id):
    data = request.get_json()
    new_status = data.get('status') 
    
    if new_status not in ['Approved', 'Pending']:
        return jsonify({"message": "Invalid status option"}), 400

    company = CompanyProfile.query.get_or_404(company_id)
    company.status = new_status
    db.session.commit()

    return jsonify({"message": f"Company status updated successfully to {new_status}"}), 200


# 3. Dedicated Fetch Route for Global Placement Drives Pipeline
@admin_bp.route('/drives', methods=['GET'])
@admin_required()
def get_all_drives():
    try:
        drives = PlacementDrive.query.all()
        drives_data = []
        
        for d in drives:
            # Safely check for 'application_deadline' first, then 'deadline', then None
            raw_deadline = getattr(d, 'application_deadline', getattr(d, 'deadline', None))
            
            # Convert to string safely to prevent 500 errors
            safe_deadline = str(raw_deadline) if raw_deadline else "N/A"
            
            drives_data.append({
                "id": d.id, 
                "job_title": getattr(d, 'job_title', 'Unknown Role'), 
                "salary": getattr(d, 'salary', 0), 
                "deadline": safe_deadline,
                "status": getattr(d, 'status', 'Pending') or 'Pending'
            })
            
        return jsonify(drives_data), 200
        
    except Exception as e:
        print("--- CRITICAL ERROR FETCHING DRIVES ---")
        traceback.print_exc() # Prints exact line of failure to terminal
        return jsonify({"message": f"Server crash: {str(e)}"}), 500


# 4. Placement Drive Management (Approve / Reject / Close)
@admin_bp.route('/drives/<int:drive_id>/status', methods=['PATCH'])
@admin_required()
def update_drive_status(drive_id):
    data = request.get_json()
    new_status = data.get('status') 
    
    if new_status not in ['Approved', 'Pending', 'Closed']:
        return jsonify({"message": "Invalid drive status option"}), 400

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = new_status
    db.session.commit()

    return jsonify({"message": f"Placement drive status updated to {new_status}"}), 200


# 5. Search and Filter Companies
@admin_bp.route('/search/companies', methods=['GET'])
@admin_required()
def search_companies():
    name_query = request.args.get('name', '')
    industry_query = request.args.get('industry', '')

    query = CompanyProfile.query
    if name_query:
        query = query.filter(CompanyProfile.company_name.ilike(f"%{name_query}%"))
    if industry_query:
        query = query.filter(CompanyProfile.industry.ilike(f"%{industry_query}%"))

    results = query.all()
    companies_data = [{
        "id": c.id,
        "company_name": c.company_name,
        "hr_contact": c.hr_contact,
        "industry": c.industry,
        "location": c.location,
        "status": c.status
    } for c in results]

    return jsonify(companies_data), 200


# 6. Search and Filter Students
@admin_bp.route('/search/students', methods=['GET'])
@admin_required()
def search_students():
    name_query = request.args.get('name', '')
    id_query = request.args.get('id', '')
    contact_query = request.args.get('contact', '')

    query = StudentProfile.query
    if name_query:
        query = query.filter(StudentProfile.full_name.ilike(f"%{name_query}%"))
    if id_query:
        query = query.filter(StudentProfile.id == id_query)
    if contact_query:
        query = query.filter(StudentProfile.contact_number.ilike(f"%{contact_query}%"))

    results = query.all()
    students_data = [{
        "id": s.id,
        "full_name": s.full_name,
        "contact_number": s.contact_number,
        "branch": s.branch,
        "cgpa": s.cgpa,
        "graduation_year": s.graduation_year
    } for s in results]

    return jsonify(students_data), 200


# 7. Account Status Control (Blacklist / Deactivate / Reactivate Roles)
@admin_bp.route('/users/<int:profile_id>/toggle-active', methods=['PATCH'])
@admin_required()
def toggle_user_active(profile_id):
    data = request.get_json()
    target_role = data.get('role') 
    
    if target_role == 'Company':
        profile = CompanyProfile.query.get_or_404(profile_id)
        user = User.query.get(profile.user_id)
        user.is_active = not user.is_active
        profile.status = 'Blacklisted' if not user.is_active else 'Approved'
    elif target_role == 'Student':
        profile = StudentProfile.query.get_or_404(profile_id)
        user = User.query.get(profile.user_id)
        user.is_active = not user.is_active
    else:
        return jsonify({"message": "Invalid target role specify context"}), 400

    db.session.commit()
    status_str = "Activated" if user.is_active else "Blacklisted/Deactivated"
    return jsonify({"message": f"User profile has been successfully {status_str}."}), 200