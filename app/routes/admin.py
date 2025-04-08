from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify, make_response, current_app, flash

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/pending_appointments', methods=['GET'])
def pending_appointments():
    # Example data - replace with your actual data from database
    pending_appointments = [
        {
            "id": 1, 
            "student_name": "Thomas Hardy", 
            "student_id": "2020-00123",
            "email": "thomashardy@mail.com",
            "purpose": "Medical Checkup", 
            "date": "2023-06-15", 
            "time": "10:00 AM",
            "status": "pending",
            "requested_date": "2023-06-10"
        },
        {
            "id": 2, 
            "student_name": "Dominique Perrier", 
            "student_id": "2020-00456",
            "email": "dominiqueperrier@mail.com",
            "purpose": "Dental Consultation", 
            "date": "2023-06-16", 
            "time": "02:30 PM",
            "status": "pending",
            "requested_date": "2023-06-11"
        }
    ]
    
    return render_template('pending_appointments.html', 
                         appointments=pending_appointments,
                         pending_count=len(pending_appointments))

@admin_bp.route('/active_appointments', methods=['GET'])
def active_appointments():
    # Example data - replace with your actual data from database
    active_appointments = [
        {
            "id": 1, 
            "student_name": "Thomas Hardy", 
            "student_id": "2020-00123",
            "email": "thomashardy@mail.com",
            "purpose": "Medical Checkup", 
            "date": "2023-06-15", 
            "time": "10:00 AM",
            "status": "approved",
            "approved_by": "Dr. Smith",
            "approved_date": "2023-06-10"
        },
        {
            "id": 2, 
            "student_name": "Dominique Perrier", 
            "student_id": "2020-00456",
            "email": "dominiqueperrier@mail.com",
            "purpose": "Dental Consultation", 
            "date": "2023-06-16", 
            "time": "02:30 PM",
            "status": "approved",
            "approved_by": "Dr. Johnson",
            "approved_date": "2023-06-11"
        }
    ]
    
    return render_template('active_appointments.html', 
                        appointments=active_appointments,
                        approved_count=len(active_appointments))

@admin_bp.route('/reschedule_appointment/<int:appointment_id>', methods=['POST'])
def reschedule_appointment(appointment_id):
    # Handle rescheduling logic here
    pass

@admin_bp.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    # Handle cancellation logic here
    pass

@admin_bp.route('/approve_appointment/<int:appointment_id>', methods=['POST'])
def approve_appointment(appointment_id):
    # Handle approval logic here
    pass

@admin_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
def reject_appointment(appointment_id):
    # Handle rejection logic here
    pass