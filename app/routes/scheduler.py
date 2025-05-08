from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
from datetime import timedelta, date
from ..models.scheduler_models import Appointments
from flask_login import login_user, login_required, logout_user, current_user
from ..models.admin_models import Admin
import json

appointment_bp = Blueprint('appointment_bp', __name__)

@appointment_bp.route('/available_slots', methods=['GET'])
def available_slots():
    """Fetch available appointment slots."""
    slots = Appointments.get_available_slots()
    return jsonify({"available_slots": slots})

@appointment_bp.route('/existing_appointment/<string:user_id>', methods=['GET'])
def get_existing_appointment(user_id):
    """Fetch a user's existing appointment details."""
    appointment = Appointments.get_existing_appointment(user_id)

    if appointment:
        # Convert date and timedelta objects to strings
        for key, value in appointment.items():
            if isinstance(value, date):  
                appointment[key] = value.strftime("%Y-%m-%d")  
            elif isinstance(value, timedelta):  
                appointment[key] = str(value)  # Convert timedelta to string

        # ✅ Return a formatted string instead of a dictionary
        formatted_response = (
            f"Appointment Details:\n"
            f"- Date: {appointment.get('appointment_date', 'N/A')}\n"
            f"- Time: {appointment.get('appointment_time', 'N/A')}\n"
            f"- Purpose: {appointment.get('purpose', 'N/A')}\n"
            f"- Status: {appointment.get('status', 'N/A')}\n"
        )

        return jsonify({"appointment": formatted_response}) 
    else:
        return jsonify({"message": "No active appointment found."})
    
@appointment_bp.route('/schedule', methods=['POST'])
def schedule_appointment():
    """Schedule a new appointment."""
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    user_email = data.get('user_email')
    date = data.get('date')
    time = data.get('time')
    purpose = data.get('purpose', "General Checkup")

    result = Appointments.create_appointment(user_id, user_name, user_email, date, time, purpose)
    return jsonify({"message": result})

@appointment_bp.route('/cancel/<string:user_id>', methods=['POST'])
def cancel_appointment(user_id):
    """Cancel an appointment."""
    result = Appointments.cancel_appointment(user_id)
    return jsonify({"message": result})

@appointment_bp.route('/reschedule', methods=['POST'])
def reschedule_appointment():
    """Reschedule an existing appointment."""
    data = request.json
    user_id = data.get('user_id')
    new_date = data.get('new_date')
    new_time = data.get('new_time')

    result = Appointments.reschedule_appointment(user_id, new_date, new_time)
    return jsonify({"message": result})
