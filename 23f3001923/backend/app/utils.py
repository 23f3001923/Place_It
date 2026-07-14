from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from app.models import CompanyProfile, StudentProfile, User

def admin_required():
    """Decorator to restrict access exclusively to users with the Admin role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "Admin":
                return jsonify({"message": "Access restricted. Admin privileges required."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def company_required():
    """Decorator to restrict access to approved Company users whose accounts are active."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "Company":
                return jsonify({"message": "Access restricted. Company access only."}), 403
            
            user_id = get_jwt_identity()
            # Double check global user state block rule
            user = User.query.get(int(user_id))
            if not user or not user.is_active:
                return jsonify({"message": "Access denied. This account has been deactivated."}), 403

            # Context verification: Ensure the company profile is approved by Admin
            profile = CompanyProfile.query.filter_by(user_id=int(user_id)).first()
            if not profile or profile.status != 'Approved':
                return jsonify({"message": "Access denied. Your company profile is not approved by Admin."}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def student_required():
    """Decorator to restrict access to active Student users."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "Student":
                return jsonify({"message": "Access restricted. Student access only."}), 403
            
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user or not user.is_active:
                return jsonify({"message": "Access denied. This student account has been deactivated."}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator