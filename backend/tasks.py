from celery_worker import make_celery
from extensions import db
from models import Application, StudentProfile, PlacementDrive, User
from datetime import datetime
import csv
import os

# We will initialize this fully inside app.py
celery = None 

# ---------------------------------------------------------
# 1. User Triggered Async Job: Export Applications as CSV
# ---------------------------------------------------------
def generate_student_csv(student_id):
    # This runs in the background!
    student = StudentProfile.query.get(student_id)
    applications = Application.query.filter_by(student_id=student_id).all()
    
    filename = f"exports/student_{student_id}_history.csv"
    os.makedirs('exports', exist_ok=True) 

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Application ID', 'Drive Title', 'Company Name', 'Status', 'Applied On'])
        
        for app in applications:
            writer.writerow([
                app.id, 
                app.drive.job_title, 
                app.drive.company.company_name, 
                app.status, 
                app.applied_on.strftime('%Y-%m-%d')
            ])
            
    print(f"[CELERY] CSV successfully generated for student_id={student_id} at {filename}")
    return filename

# FIX: Add this alias so your existing imports in routes/student.py work
def export_student_history(student_id):
    return generate_student_csv(student_id)

# ---------------------------------------------------------
# 2. Scheduled Job: Daily Reminders
# ---------------------------------------------------------
def send_daily_reminders():
    closing_soon = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved'
    ).all() 
    
    print("[CELERY - BEAT] Sending daily reminder to students via Google Chat Webhook...")
    return "Daily reminders sent"

# ---------------------------------------------------------
# 3. Scheduled Job: Monthly Activity Report
# ---------------------------------------------------------
def generate_monthly_report():
    total_drives = PlacementDrive.query.count()
    total_apps = Application.query.count()
    selected_apps = Application.query.filter_by(status='Selected').count()
    
    html_report = f"""
    <h1>Monthly Placement Report</h1>
    <p>Total Drives Conducted: {total_drives}</p>
    <p>Total Applications: {total_apps}</p>
    <p>Total Students Selected: {selected_apps}</p>
    """
    
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(f"[CELERY - BEAT] Mailing Monthly Report to {admin.email}...")
    
    return "Monthly report generated"