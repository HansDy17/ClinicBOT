from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify, make_response, current_app, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_dance.contrib.google import google
import logging
from datetime import timedelta
from ..models.admin_models import Admin
from .. import mail

auth_bp = Blueprint('auth_bp', __name__)
logger = logging.getLogger(__name__)

# Security enhancements
def validate_login_input(username, password):
    """Validate login input to prevent basic attacks"""
    if not username or not password:
        return False, "Username and password are required"
    if len(username) > 50 or len(password) > 100:
        return False, "Input too long"
    return True, ""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            # Input validation
            is_valid, message = validate_login_input(username, password)
            if not is_valid:
                flash(message, 'error')
                return jsonify({'success': False, 'message': message}), 400
            
            # Get user data
            user_data = Admin.get_admin_data_by_username(username)
            
            if not user_data:
                logger.warning(f"Login attempt for non-existent user: {username}")
                flash('Invalid credentials', 'error')  # Generic message for security
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
            # Verify password

            if user_data['password_hash'] is None:
                logger.warning(f"Password hash not found for user: {username}")
                flash('Invalid credentials', 'error')
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
            # Create user session
            admin = Admin(user_data['id'])
            session.permanent = True
            auth_bp.session_lifetime = timedelta(minutes=30)  # Session timeout
            session['loggedin'] = True
            session['username'] = user_data['username']
            session['user_id'] = user_data['id']
            session['full_name'] = user_data['full_name']
            session['_fresh'] = True  # For Flask-Login
            
            login_user(admin, remember=request.form.get('remember') == 'on')
            
            logger.info(f"Admin {username} logged in successfully")
            flash('Login successful!', 'success')
            return jsonify({
                'success': True,
                'redirect': url_for('admin_bp.pending_appointments') 
            })
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}", exc_info=True)
            flash('An error occurred during login. Please try again.', 'error')
            return jsonify({
                'success': False, 
                'message': 'An error occurred during login. Please try again.'
            }), 500
    
    # GET request - show login form
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.pending_appointments'))
    
    return render_template("auth.html", user=current_user)

# auth_bp.py
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            id_number = request.form.get('id_number', '').strip()

            # Basic validation
            if not all([name, email, id_number]):
                flash('All fields are required', 'error')
                return redirect(url_for('auth_bp.signup'))
            
            
            
            Admin.create_user_account(full_name=name, email=email, id_number=id_number)
            user_data = Admin.get_user_data_by_username(name)            
            print("1")
            admin = Admin(user_data['id'])
            session.permanent = True
            auth_bp.session_lifetime = timedelta(minutes=30)  # Session timeout
            session['loggedin'] = True
            session['username'] = user_data['user_name']
            session['user_id'] = user_data['id']
            session['_fresh'] = True  # For Flask-Login
            login_user(admin, remember=request.form.get('remember') == 'on')                              
            print("2")

            logger.info(f"User {name} signed up successfully")
            flash('Account created and logged in!', 'success')
            return redirect(url_for('index_bp.Index'))

        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            flash('Error creating account', 'error')
            return redirect(url_for('auth_bp.signup'))

    # GET request - show signup form
    return render_template("sign-up.html")

@auth_bp.route('/google-login')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info from Google", 400
    
    google_info = resp.json()
    email = google_info["email"]
    
    # Verify university domain
    if not email.endswith("@msuiit.edu.ph"):  # Change to your domain
        logout_user()
        flash("Only university Google accounts are allowed", "error")
        return redirect(url_for("auth_bp.login"))
    
    # Find or create user
    user = User.get_user_data_by_email(email)
    if not user:
        # Create new user
        user = User.create_google_user(google_info)
    
    login_user(user)
    return redirect(url_for("index_bp.dashboard"))

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        username = session.get('username', 'unknown')
        logout_user()
        session.clear()  # Clear all session data
        logger.info(f"User {username} logged out successfully")
        flash('You have been logged out successfully.', 'success')
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}", exc_info=True)
        flash('An error occurred during logout.', 'error')
    
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    flash('Please contact your super admin to reset password.', 'warning')
    return redirect(url_for('auth_bp.login'))
