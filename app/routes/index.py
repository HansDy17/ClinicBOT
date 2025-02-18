from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify, session
import mysql.connector
from datetime import datetime # add the date of student added
from ..agents.agent_team import agent_team, clinic_agent
from ..agents.test4 import agent
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
# from ..models import *
import os

index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/')
def Index():

    return render_template('index.html')

@index_bp.route('/insert', methods = ['POST', 'GET'])
def insert():
    pass

@index_bp.route("/get", methods=["POST"])
def chatbot_response():
    try:
        question = request.form.get('msg')  # Extract from form data
        
        if not question:
            return jsonify("Error: No question provided"), 400
        
        response = agent.run(question)
        return jsonify(response.content)  # Return just the text, not an object
    
    except Exception as e:
        return jsonify(f"Error: {str(e)}"), 500