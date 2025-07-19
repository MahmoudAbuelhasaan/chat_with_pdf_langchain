import os
import uuid
from datetime import datetime
from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.chat import bp
from app.models import PdfFile
from app.utilits import allowed_file


@bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        file = request.files.get('pdfFile')

        if not file or file.filename == '':
            flash('Please select a file to upload.', 'warning')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Only PDF files are allowed.', 'danger')
            return redirect(request.url)

        try:
            pdf = PdfFile(user_id=current_user.id)
            pdf.upload_file(file)
            db.session.add(pdf)
            db.session.commit()
            flash(f'File "{file.filename}" uploaded successfully!', 'success')
            return redirect(url_for('chat.home'))
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'danger')
            return redirect(request.url)


    uploaded_pdfs = PdfFile.query.filter_by(user_id=current_user.id).order_by(PdfFile.uploaded_at.desc()).all()
    return render_template('chat/home.html', uploaded_pdfs=uploaded_pdfs)


@bp.route('/chat', methods=['GET', 'POST']) 
@login_required
def chat():

    return render_template('chat/chat.html')
    