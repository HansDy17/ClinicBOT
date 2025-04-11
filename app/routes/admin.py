from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify, make_response, current_app, flash
from flask_mail import Message
from ..import mail
from ..models.admin_models import Appointment

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/pending_appointments', methods=['GET'])
def pending_appointments():
    appointments = Appointment.get_pending_appointments()
    return render_template('pending_appointments.html', 
                         appointments=appointments,
                         pending_count=len(appointments))

@admin_bp.route('/active_appointments', methods=['GET'])
def active_appointments():
    appointments = Appointment.get_active_appointments()
    return render_template('active_appointments.html', 
                         appointments=appointments,
                         approved_count=len(appointments))

@admin_bp.route('/approve_appointment/<int:appointment_id>', methods=['POST'])
def approve_appointment(appointment_id):
    try:
        approved_by = session.get('admin_name', 'Admin')
        Appointment.approve_appointment(appointment_id, approved_by)
        flash('Appointment approved successfully', 'success')
    except Exception as e:
        flash(f'Error approving appointment: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.pending_appointments'))

def send_email(to, subject, body):
    msg = Message(subject, sender="your@gmail.com", recipients=[to])
    msg.body = body
    mail.send(msg)

# Example in a route
@admin_bp.route("/approve_appointment/<email>")
def approve(email):
    send_email(email, "Approved!", "Your appointment is confirmed.")
    return "Email sent!"