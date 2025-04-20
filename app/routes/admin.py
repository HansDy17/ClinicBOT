from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify, make_response, current_app, flash
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
from ..import mail
from ..models.admin_models import Appointment, Admin

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/pending_appointments', methods=['GET'])
@login_required
def pending_appointments():
    appointments = Appointment.get_pending_appointments()
    admin = Admin.get_admin_data_by_username(session['username'])
    return render_template('pending_appointments.html', 
                         appointments=appointments,
                         admin=admin,
                         pending_count=len(appointments))

@admin_bp.route('/active_appointments', methods=['GET'])
@login_required
def active_appointments():
    appointments = Appointment.get_active_appointments()
    admin = Admin.get_admin_data_by_username(session['username'])
    return render_template('active_appointments.html', 
                         appointments=appointments,
                         admin=admin,
                         approved_count=len(appointments))

@admin_bp.route('/approve_appointment/<int:appointment_id>', methods=['POST'])
def approve_appointment(appointment_id):
    # if 'admin_name' not in session:
    #     flash('Unauthorized', 'danger')
    #     return redirect(url_for('auth_bp.admin_login'))
    
    notes = request.form.get('approval_notes', 'No notes provided')
    try:
        approved_by = session['admin_name']
        Appointment.approve_appointment(appointment_id, approved_by,notes)
        flash('Approved successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.pending_appointments'))

@admin_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
def reject_appointment(appointment_id):
    # if 'admin_name' not in session:
    #     flash('Unauthorized', 'danger')
    #     return redirect(url_for('auth_bp.admin_login')) #Goods nani diri!
    
    reason = request.form.get('rejection_reason', 'No reason provided')
    try:
        rejected_by = session['admin_name']
        Appointment.reject_appointment(appointment_id, rejected_by, reason)
        flash('Rejected successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
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