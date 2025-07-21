# app/chat/apis.py

import uuid
from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user
from app import db, socketio
from app.chat import bp
from app.models import PdfFile
from app.utilits import allowed_file
from app.AI.ai import initialize_pdf_chat

# ---------- Helpers ----------

def get_user_pdfs():
    """Return list of user's uploaded PDFs ordered by date."""
    return PdfFile.query.filter_by(user_id=current_user.id).order_by(PdfFile.uploaded_at.desc()).all()


def get_pdf_or_404(pdf_id):
    """Fetch PDF by ID or return 404 if not found or access denied."""
    pdf = PdfFile.query.get(pdf_id)
    if not pdf or pdf.user_id != current_user.id:
        flash("PDF not found or access denied.", "danger")
        return None
    return pdf


# ---------- Routes ----------

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
            return redirect(url_for('chat.chat_with_pdf', pdf_id=pdf.id))
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'danger')
            return redirect(request.url)

    uploaded_pdfs = get_user_pdfs()
    return render_template('chat/home.html', uploaded_pdfs=uploaded_pdfs)


@bp.route('/chat')
@login_required
def chat():
    """Fallback chat route — if no PDF, fetch latest uploaded."""
    pdf = PdfFile.query.filter_by(user_id=current_user.id).order_by(PdfFile.uploaded_at.desc()).first()
    if not pdf:
        flash("No PDFs found. Please upload one to start chatting.", "warning")
        return redirect(url_for("chat.home"))
    return redirect(url_for("chat.chat_with_pdf", pdf_id=pdf.id))


@bp.route('/chat/<int:pdf_id>', methods=['GET'])
@login_required
def chat_with_pdf(pdf_id):
    pdf = get_pdf_or_404(pdf_id)
    if not pdf:
        return redirect(url_for("chat.home"))
    return render_template("chat/chat.html", pdf=pdf)



# ---------- Socket.IO Event ----------

@socketio.on('message')
@login_required
def handle_message(data):
    user_message = data.get('message')
    pdf_id = data.get('pdf_id')
    session_id = str(current_user.id)

    if not user_message or not pdf_id:
        socketio.emit('response', {'response': "Missing message or PDF ID."})
        return

    pdf = PdfFile.query.get(pdf_id)
    if not pdf or pdf.user_id != current_user.id:
        socketio.emit('response', {'response': "Invalid PDF or access denied."})
        return

    try:
        pdf_path = f"app/{pdf.filepath}"
        agent = initialize_pdf_chat(pdf_path, session_id)

        response = agent.invoke(
            {"input": user_message},
            config={
                "configurable": {
                    "session_id": session_id
                }
            }
        )


        # socketio.emit('response', {'response': response.get('output', 'No response')})
        socketio.emit('response', {'response': str(response.content)})
    except Exception as e:
        socketio.emit('response', {'response': f"Error processing message: {str(e)}"})
