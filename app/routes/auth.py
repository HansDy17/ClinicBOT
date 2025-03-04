from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify, make_response
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import json
import os

auth_bp = Blueprint('auth_bp', __name__)

# Load SAML configuration
# def load_saml_settings():
#     with open("saml_settings.json") as f:
#         return json.load(f)

# saml_settings = load_saml_settings()

# Helper function to initialize SAML Auth
def prepare_saml_request(req):
    return OneLogin_Saml2_Auth(req, saml_settings)

@auth_bp.route("/login")
def login():
    # req = {
    #     "https_host": request.host_url,
    #     "script_name": request.path,
    #     "get_data": request.args,
    #     "post_data": request.form,
    # }
    
    # auth = prepare_saml_request(req)
    return render_template("auth.html")

@auth_bp.route("/sso/", methods=["POST"])
def sso():
    req = {
        "https_host": request.host_url,
        "script_name": request.path,
        "get_data": request.args,
        "post_data": request.form,
    }
    
    auth = prepare_saml_request(req)
    auth.process_response()
    
    errors = auth.get_errors()
    if errors:
        return f"Error: {errors}", 400

    if not auth.is_authenticated():
        return "Authentication failed", 401

    # Get user email
    user_data = auth.get_attributes()
    email = user_data.get("email", [""])[0]

    # Restrict login to university email only
    if not email.endswith("@g.msuiit.edu.ph"):
        return "Access denied: Please use your university emails.", 403

    session["user_email"] = email
    return redirect(url_for("index_bp.Index"))

@auth_bp.route("/logout")
def logout():
    req = {
        "https_host": request.host_url,
        "script_name": request.path,
        "get_data": request.args,
        "post_data": request.form,
    }

    auth = prepare_saml_request(req)
    return redirect(auth.logout())
