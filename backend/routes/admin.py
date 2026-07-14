# backend/routes/admin.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, CompanyProfile, StudentProfile, PlacementDrive

admin_bp = Blueprint('admin', __name__)

def is_admin(identity):
    return identity.get('role') == 'admin'

@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_stats():
    if not is_admin(get_jwt_identity()):
        return jsonify({"message": "Unauthorized"}), 403

    stats = {
        "total_students": StudentProfile.query.count(),
        "total_companies": CompanyProfile.query.count(),
        "total_drives": PlacementDrive.query.count()
    }
    return jsonify(stats), 200

@admin_bp.route('/company/<int:comp_id>/status', methods=['PUT'])
@jwt_required()
def update_company_status(comp_id):
    if not is_admin(get_jwt_identity()):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400
    company = CompanyProfile.query.get_or_404(comp_id)
    status = data.get('status')
    if not status:
        return jsonify({"message": "Status is required."}), 400

    company.approval_status = status
    db.session.commit()

    return jsonify({"message": f"Company status updated to {company.approval_status}"}), 200

@admin_bp.route('/drive/<int:drive_id>/status', methods=['PUT'])
@jwt_required()
def update_drive_status(drive_id):
    if not is_admin(get_jwt_identity()):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Invalid JSON payload."}), 400
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = data.get('status') # 'Approved', 'Rejected'
    db.session.commit()

    return jsonify({"message": f"Drive status updated to {drive.status}"}), 200

@admin_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_approvals():
    if not is_admin(get_jwt_identity()):
        return jsonify({"message": "Unauthorized"}), 403

    # Fetch companies and drives waiting for approval
    pending_companies = CompanyProfile.query.filter_by(approval_status='Pending').all()
    pending_drives = PlacementDrive.query.filter_by(status='Pending').all()

    comp_result = [{"id": c.id, "name": c.company_name, "hr": c.hr_contact} for c in pending_companies]
    drive_result = [{"id": d.id, "company": d.company.company_name, "title": d.job_title} for d in pending_drives]

    return jsonify({"companies": comp_result, "drives": drive_result}), 200