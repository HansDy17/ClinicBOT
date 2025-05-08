from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify, session, Response, stream_with_context
from ..agents.scheduler_agent import get_agent
from flask_login import login_user, login_required, logout_user, current_user
from ..models.admin_models import User, Admin
import os

index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/')
@login_required
def Index():
    id = getattr(current_user, 'id', None)
    print(f"User Name: {id}")
    user = Admin.get_user_data_by_user_id(id)
    return render_template('index.html', user=user)

@index_bp.route("/get", methods=["POST"])
def chatbot_response():
    try:
        question = request.form.get("msg")
        if not question:
            return jsonify("Error: No question provided"), 400
        id = getattr(current_user, 'id', None)
        print(f"User Name: {id}")
        user = Admin.get_user_data_by_user_id(id)
        user_id = user['user_id']
        user_name = user['user_name']
        user_email = user['user_email']
        print("User ID:", user['id'])
        print("User Name:", user['user_name'])
        print("User Email:", user['user_email'])        

        def generate():
            response = get_agent(user_id, user_name, user_email).run(question, stream=True)
            for chunk in response:
                if hasattr(chunk, "content"):
                    formatted = chunk.content.lstrip().replace("\n", "<br>")
                    yield formatted

        return Response(stream_with_context(generate()), content_type="text/plain")

    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500
