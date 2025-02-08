from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
import mysql.connector
from datetime import datetime # add the date of student added
# from ..models import *
import os

index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/')
def Index():

    return render_template('base.html')

@index_bp.route('/insert', methods = ['POST', 'GET'])
def insert():
    if request.method == "POST":
        try:
            id = request.form['idnum']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            course = request.form['course']
            year = request.form['year']
            gender = request.form['gender']
            id_upload = request.files.get('id_upload')
            result_url = None

            if 'id_upload' in request.files:
                if id_upload.filename != '':
                    allowed_ext = {'png', 'jpeg', 'jpg'}
                    if '.' in id_upload.filename and id_upload.filename.rsplit('.', 1)[1].lower() in allowed_ext:
                        if id_upload.content_length > 10 * 1024 * 1024:  # 10 MB limit
                            flash('Image size should be 30 MB or below.', 'error')
                        else:
                            print(f"Cloud Name: {cloudinary.config().cloud_name}")
                            print(f"API Key: {cloudinary.config().api_key}")
                            print(f"API Secret: {cloudinary.config().api_secret}")
                            result = cloudinary.uploader.upload(id_upload)
                            result_url = result["secure_url"]
                    else:
                         flash('Invalid file format for image. Please upload a valid image.', 'error')
                         return redirect(url_for('index_bp.Index'))

            Students.addStudent(id, firstname, lastname, course, year, gender, result_url)
            flash("Data inserted successfully!", "success")
        except mysql.connector.IntegrityError as e:
            flash("Error: This ID already exists. Please use a unique ID.", "error")
        return redirect(url_for('index_bp.Index'))

@index_bp.route('/update', methods=['POST', 'GET'])
def update():
    if request.method=='POST':
        try:
            # init_id = request.form['id']
            id = request.form['idnum']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            course = request.form['course']
            year = request.form['year']
            gender = request.form['gender']
            id_upload = request.files.get('id_upload')
            result_url = None

            if 'id_upload' in request.files:
                if id_upload.filename != '':
                    allowed_ext = {'png', 'jpeg', 'jpg'}
                    if '.' in id_upload.filename and id_upload.filename.rsplit('.', 1)[1].lower() in allowed_ext:
                        if id_upload.content_length > 30 * 1024 * 1024:  # 30 MB limit
                            flash('Image size should be 30 MB or below.', 'error')
                        else:
                            print(f"Cloud Name: {cloudinary.config().cloud_name}")
                            print(f"API Key: {cloudinary.config().api_key}")
                            print(f"API Secret: {cloudinary.config().api_secret}")
                            result = cloudinary.uploader.upload(id_upload)
                            result_url = result["secure_url"]
                    else:
                         flash('Invalid file format for image. Please upload a valid image.', 'error')
                         return redirect(url_for('index_bp.Index'))
                                
            Students.editStudent(id, firstname, lastname, course, year, gender, result_url)
            flash("Data Updated Successfully!")
            return redirect(url_for('index_bp.Index'))
        except mysql.connector.IntegrityError as e:
            flash("Error: This ID already exists. Please use a unique ID.", "error")
    return redirect(url_for('index_bp.Index'))
    
@index_bp.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete(id):
    Students.deleteStudent(id)
    flash("Data deleted Successfully!")
    return redirect(url_for('index_bp.Index'))

@index_bp.route('/search/<string:id>', methods=['POST', 'GET'])
def search(id):
    if request.method=='POST':
        id = request.form['search']
        data =  Students.searchStudent(id)        
    
    return render_template('student.html', result =data)