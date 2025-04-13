from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify, make_response, current_app, flash
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import logging
from datetime import timedelta

auth_bp = Blueprint('auth_bp', __name__)

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
            user_data = User.get_user_by_username(username)
            
            if not user_data:
                logger.warning(f"Login attempt for non-existent user: {username}")
                flash('Invalid credentials', 'error')  # Generic message for security
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
            # Verify password
            stored_password_hash = user_data['password_hash']
            if not check_password_hash(stored_password_hash, password):
                logger.warning(f"Failed login attempt for user: {username}")
                flash('Invalid credentials', 'error')
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
            # Check if account is locked or needs other verification
            if user_data.get('is_locked', False):
                flash('Account is locked. Please contact support.', 'error')
                return jsonify({'success': False, 'message': 'Account locked'}), 403
            
            # Create user session
            user = User(user_data['id'])
            session.permanent = True
            auth_bp.session_lifetime = timedelta(minutes=30)  # Session timeout
            session['loggedin'] = True
            session['username'] = user_data['username']
            session['user_id'] = user_data['id']
            session['_fresh'] = True  # For Flask-Login
            
            login_user(user, remember=request.form.get('remember') == 'on')
            
            logger.info(f"User {username} logged in successfully")
            flash('Login successful!', 'success')
            return jsonify({
                'success': True,
                'redirect': url_for('admin_bp.pending_appointments')  # Redirect to dashboard after login
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
    # Implement password reset functionality
    pass


# SAML Authentication
def init_saml_auth(req):
    """Initialize SAML Authentication using Flask's Config"""
    saml_path = current_app.config["SAML_PATH"]  # Access Flask config
    return OneLogin_Saml2_Auth(req, custom_base_path=saml_path)

def prepare_flask_request(request):
    return {
        "https": "on" if request.scheme == "https" else "off",
        "http_host": request.host,
        "script_name": request.path,
        "get_data": request.args.copy(),
        "post_data": request.form.copy(),
    }

@auth_bp.route("/index", methods=["GET", "POST"])
def index():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    errors = []
    error_reason = None
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    if "sso" in request.args:
        return redirect(auth.login())
        # If AuthNRequest ID need to be stored in order to later validate it, do instead
        # sso_built_url = auth.login()
        # request.session['AuthNRequestID'] = auth.get_last_request_id()
        # return redirect(sso_built_url)
    elif "sso2" in request.args:
        return_to = "%sattrs/" % request.host_url
        return redirect(auth.login(return_to))
    elif "slo" in request.args:
        name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
        if "samlNameId" in session:
            name_id = session["samlNameId"]
        if "samlSessionIndex" in session:
            session_index = session["samlSessionIndex"]
        if "samlNameIdFormat" in session:
            name_id_format = session["samlNameIdFormat"]
        if "samlNameIdNameQualifier" in session:
            name_id_nq = session["samlNameIdNameQualifier"]
        if "samlNameIdSPNameQualifier" in session:
            name_id_spnq = session["samlNameIdSPNameQualifier"]

        return redirect(auth.logout(name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq))
    elif "acs" in request.args:
        request_id = None
        if "AuthNRequestID" in session:
            request_id = session["AuthNRequestID"]

        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            if "AuthNRequestID" in session:
                del session["AuthNRequestID"]
            session["samlUserdata"] = auth.get_attributes()
            session["samlNameId"] = auth.get_nameid()
            session["samlNameIdFormat"] = auth.get_nameid_format()
            session["samlNameIdNameQualifier"] = auth.get_nameid_nq()
            session["samlNameIdSPNameQualifier"] = auth.get_nameid_spnq()
            session["samlSessionIndex"] = auth.get_session_index()
            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if "RelayState" in request.form and self_url != request.form["RelayState"]:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the request.form['RelayState'] is a trusted URL.
                return redirect(auth.redirect_to(request.form["RelayState"]))
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()
    elif "sls" in request.args:
        request_id = None
        if "LogoutRequestID" in session:
            request_id = session["LogoutRequestID"]
        dscb = lambda: session.clear()
        url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the url is a trusted URL.
                return redirect(url)
            else:
                success_slo = True
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    if "samlUserdata" in session:
        paint_logout = True
        if len(session["samlUserdata"]) > 0:
            attributes = session["samlUserdata"].items()

    return render_template("index1.html", errors=errors, error_reason=error_reason, not_auth_warn=not_auth_warn, success_slo=success_slo, attributes=attributes, paint_logout=paint_logout)


# 🔹 Initiate SAML login
@auth_bp.route('/saml_login/')
def saml_login():
    auth = prepare_flask_request(request) 
    flash('Logged out successfully', 'success')
    return redirect(url_for('index_bp.Index'))

# 🔹 Process SAML response after login
@auth_bp.route('/sso/', methods=['POST'])
def sso():
    auth = prepare_flask_request(request)
    auth.process_response()
    
    errors = auth.get_errors()
    if errors:
        return f"Error: {errors}", 400

    if not auth.is_authenticated():
        return "Authentication failed", 401

    user_data = auth.get_attributes()
    email = user_data.get("email", [""])[0]

    # Restrict login to university emails only
    if not email.endswith("@university.edu"):
        return "Access denied: Only university emails allowed.", 403

    session["user_email"] = email
    return redirect(url_for("auth_bp.index"))

@auth_bp.route("/metadata/")
def metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if not errors:
        resp = make_response(metadata, 200)
        resp.headers["Content-Type"] = "text/xml"
    else:
        resp = make_response(", ".join(errors), 500)
    return resp
