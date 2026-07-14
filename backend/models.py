# backend/models.py
from extensions import db
from datetime import datetime

# 1. UNIFIED USER MODEL
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'company', 'student'
    is_active = db.Column(db.Boolean, default=True) # For blacklisting/deactivating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade="all, delete-orphan")

# 2. COMPANY PROFILE
class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(150))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    approval_status = db.Column(db.String(20), default='Pending') # Pending / Approved / Rejected / Blacklisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)
    placements = db.relationship('Placement', backref='company', lazy=True)

# 3. STUDENT PROFILE
class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    passing_year = db.Column(db.Integer, nullable=False)
    resume_url = db.Column(db.String(255)) # URL or path to uploaded resume
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience_years = db.Column(db.Float)
    contact_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='student', lazy=True)
    placements = db.relationship('Placement', backref='student', lazy=True)

# 4. PLACEMENT DRIVE
class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_branch = db.Column(db.String(100)) # e.g., "CSE, IT"
    eligibility_cgpa = db.Column(db.Float, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending / Approved / Closed
    salary = db.Column(db.String(100))
    skills_required = db.Column(db.Text)
    experience_required = db.Column(db.String(100))
    benefits = db.Column(db.Text)
    location = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='drive', lazy=True)
    placements = db.relationship('Placement', backref='drive', lazy=True)

# 5. APPLICATION RECORD
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    status = db.Column(db.String(20), default='Applied') # Applied / Shortlisted / Interview / Selected / Rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    interview_date = db.Column(db.DateTime)
    company_feedback = db.Column(db.Text)
    student_feedback = db.Column(db.Text)

    # Ensure a student can only apply ONCE to a specific drive
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='_student_drive_uc'),)

# 6. PLACEMENT RECORD
class Placement(db.Model):
    __tablename__ = 'placements'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100))
    joining_date = db.Column(db.DateTime)
    status = db.Column(db.String(30), default='Placed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
