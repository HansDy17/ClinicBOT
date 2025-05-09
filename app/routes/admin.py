from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify, make_response, current_app, flash
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
from ..import mail
from ..models.admin_models import Appointment, Admin
import os
from werkzeug.utils import secure_filename


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
@login_required
def approve_appointment(appointment_id):
    notes = request.form.get('approval_notes')
    try:
        admin = Admin.get_admin_data_by_username(session['username'])
        approved_by = getattr(current_user, 'full_name', None) or current_user.username
        print(approved_by)
        Appointment.approve_appointment(appointment_id, approved_by,notes)
        flash('Approved successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.pending_appointments'))

@admin_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def reject_appointment(appointment_id):
    reason = request.form.get('rejection_reason')
    try:
        admin = Admin.get_admin_data_by_username(session['username'])
        rejected_by = getattr(current_user, 'full_name', None) or current_user.username
        Appointment.reject_appointment(appointment_id, rejected_by, reason)
        flash('Rejected successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.pending_appointments'))

@admin_bp.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    reason = request.form.get('cancel_reason')
    try:
        admin = Admin.get_admin_data_by_username(session['username'])
        cancelled_by = getattr(current_user, 'full_name', None) or current_user.username
        Appointment.cancel_appointment(appointment_id, cancelled_by, reason)
        flash('Cancelled successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.active_appointments'))

@admin_bp.route('/reschedule_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def reschedule_appointment(appointment_id):
    new_date = request.form.get('new_date')
    new_time = request.form.get('new_time')
    reason = request.form.get('reschedule_reason')
    try:
        Appointment.reschedule_appointment(appointment_id, new_date, new_time, reason)
        flash('Cancelled successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.active_appointments'))

def send_action_email(recipient_email, action_type, appointment_details=None, admin_name=None):
    try:
        email_config = {
            'approve': {
                'subject': "Appointment Approved - MSU-IIT Clinic",
                'template': 'emails/approve_appointment.html'
            },
            'reject': {
                'subject': "Appointment Rejected - MSU-IIT Clinic",
                'template': 'emails/reject_appointment.html'
            },
            'cancel': {
                'subject': "Appointment Cancelled - MSU-IIT Clinic",
                'template': 'emails/cancel_appointment.html'
            },
            'reschedule': {
                'subject': "Appointment Rescheduled - MSU-IIT Clinic",
                'template': 'emails/reschedule_appointment.html'
            }
        }

        config = email_config.get(action_type.lower())
        if not config:
            raise ValueError(f"Invalid action type: {action_type}")

        msg = Message(
            subject=config['subject'],
            recipients=[recipient_email]
        )
        msg.html = render_template(
            config['template'],
            appointment_details=appointment_details,
            admin_name=admin_name,
            clinic_name="MSU-IIT Clinic",
            contact_info="mdhs@g.msuiit.edu.ph"
        )

        mail.send(msg)
        current_app.logger.info(f"{action_type} email sent to {recipient_email}")
    except Exception as e:
        current_app.logger.error(f"Error sending {action_type} email: {e}")

@admin_bp.route('/staff_management', methods=['GET'])
@login_required
def staff_management():
    staff_members = Admin.get_all_staff()
    admin = Admin.get_admin_data_by_username(session['username'])
    return render_template('staff_management.html', 
                         staff_members=staff_members,
                         admin=admin,
                         roles=['nurse', 'doctor', 'staff'])

@admin_bp.route('/add_staff', methods=['POST'])
@login_required
def add_staff():
    if request.method == 'POST':
        try:
            staff_id = request.form['staff_id']
            full_name = request.form['full_name']
            email = request.form['email']
            role = request.form['role']
            
            Admin.create_staff(staff_id, full_name, email, role)
            flash('Staff member added successfully', 'success')
        except Exception as e:
            flash(f'Error adding staff: {str(e)}', 'danger')
            current_app.logger.error(f"Database error: {str(e)}")  # Add logging
        return redirect(url_for('admin_bp.staff_management'))
    
@admin_bp.route('/update_staff', methods=['POST'])
@login_required
def update_staff():
    if request.method == 'POST':
        try:
            staff_id = request.form['staff_id']
            full_name = request.form['full_name']
            email = request.form['email']
            role = request.form['role']

            # Get current staff data
            current_staff = Admin.get_staff_by_id(staff_id)
            if not current_staff:
                flash('Staff member not found', 'danger')
                return redirect(url_for('admin_bp.staff_management'))

            Admin.update_staff(staff_id, full_name, email, role)
            flash('Staff member updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating staff: {str(e)}', 'danger')
            current_app.logger.error(f"Database error: {str(e)}")  # Add logging
        return redirect(url_for('admin_bp.staff_management'))

@admin_bp.route('/delete_staff', methods=['POST'])
@login_required
def delete_staff():
    try:
        staff_id = request.form['staff_id']
        Admin.delete_staff(staff_id)
        flash('Staff member deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting staff: {str(e)}', 'danger')
        current_app.logger.error(f"Database error: {str(e)}")  # Add logging
    return redirect(url_for('admin_bp.staff_management'))