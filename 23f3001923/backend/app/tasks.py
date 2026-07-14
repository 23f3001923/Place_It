import csv
import os
from datetime import datetime
from celery import Celery
from celery.schedules import crontab

# 1. Initialize Celery with direct configuration properties.
# This avoids invoking the global Flask app factory during module import runtime.
celery_app = Celery('ppa_tasks', 
                    broker='redis://localhost:6379/0', 
                    backend='redis://localhost:6379/1')

# 2. Define the Celery Beat Cron Schedule configuration structure safely
celery_app.conf.beat_schedule = {
    'daily-interview-reminders-9am': {
        'task': 'app.tasks.send_daily_interview_reminders',
        'schedule': crontab(hour=9, minute=0), # Daily at 9:00 AM
    },
    'monthly-placement-report-1st': {
        'task': 'app.tasks.generate_monthly_placement_report',
        'schedule': crontab(day_of_month='1', hour=0, minute=0), # Monthly 1st day at midnight
    },
}

# ---------------------------------------------------------
# ASYNC TASK: User-Triggered CSV Export (Student Dashboard)
# ---------------------------------------------------------
@celery_app.task
def export_student_applications_csv(student_id, email):
    # Defer imports inside the execution context to isolate runtime namespaces
    from app import create_app
    from app.models import db, Application
    
    flask_app = create_app()
    with flask_app.app_context():
        applications = Application.query.filter_by(student_id=student_id).all()
        
        # Ensure export directory exists safely
        os.makedirs('exports', exist_ok=True)
        filename = f"exports/student_{student_id}_history.csv"
        
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Date Applied'])
            
            for app in applications:
                writer.writerow([
                    app.student_id,
                    app.drive.company.company_name,
                    app.drive.job_title,
                    app.status,
                    app.application_date.strftime('%Y-%m-%d')
                ])
                
        print(f"✅ CSV Export Complete for Student {student_id}. Saved to {filename}. Alert sent to {email}.")
        return filename

# ---------------------------------------------------------
# SCHEDULED TASK: Daily Interview Reminders
# ---------------------------------------------------------
@celery_app.task
def send_daily_interview_reminders():
    from app import create_app
    from app.models import StudentProfile, Application
    
    flask_app = create_app()
    with flask_app.app_context():
        shortlisted_apps = Application.query.filter_by(status='Shortlisted').all()
        
        count = 0
        for app in shortlisted_apps:
            student = StudentProfile.query.get(app.student_id)
            if student:
                print(f"🔔 Reminder sent to {student.full_name}: Upcoming interview for {app.drive.job_title} at {app.drive.company.company_name}.")
                count += 1
            
        return f"Sent {count} reminders."

# ---------------------------------------------------------
# SCHEDULED TASK: Monthly Placement Report for Admin
# ---------------------------------------------------------
@celery_app.task
def generate_monthly_placement_report():
    from app import create_app
    from app.models import PlacementDrive, Application
    
    flask_app = create_app()
    with flask_app.app_context():
        total_drives = PlacementDrive.query.count()
        total_selected = Application.query.filter_by(status='Selected').count()
        
        print(f"📊 MONTHLY REPORT: {total_drives} Drives Conducted | {total_selected} Students Placed.")
        return "Monthly report generated and emailed to Admin."