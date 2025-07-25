import os
from app import db
from app import bcrypt  # correct spelling
from flask_login import UserMixin
from datetime import datetime
import uuid

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password, password)
    


class PdfFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('pdf_files'))

    def upload_file(self, file):
        print("Uploading file:", file)
        self.filename = file.filename
        print("Original filename:", self.filename)
        unique_id = uuid.uuid4().hex
        filename_parts = file.filename.rsplit('.', 1)
        print("Filename parts:", filename_parts)
        if len(filename_parts) == 2:
            name, ext = filename_parts
            print("Name:", name, "Extension:", ext)
            new_filename = f"{name}_{unique_id}.{ext}"
        else:
            new_filename = f"{file.filename}_{unique_id}"

        uploads_dir = os.path.join('app', 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        self.filepath = os.path.join('static', 'uploads', new_filename)
        full_path = os.path.join('app', self.filepath)

        file.save(full_path)
        self.uploaded_at = datetime.utcnow()



class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('chat_messages', lazy=True))

    message = db.Column(db.Text, nullable=False)
    is_user = db.Column(db.Boolean, nullable=False, default=True)  

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    chat_session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)



class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('chat_sessions', lazy=True))

    pdf_id = db.Column(db.Integer, db.ForeignKey('pdf_file.id'), nullable=False)
    pdf = db.relationship('PdfFile', backref=db.backref('chat_sessions', lazy=True))

    messages = db.relationship('ChatMessage', backref='chat_session', cascade='all, delete-orphan')

