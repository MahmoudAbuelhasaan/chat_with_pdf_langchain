from flask import render_template,redirect,request,flash,url_for
from flask_login import current_user,login_required,login_user,logout_user
from app.auth.forms import LoginForm, RegisterForm
from app.models import User
from app import db
from app.chat import bp

@bp.route('/home', methods=['GET', 'POST'])
def home():

    return render_template('chat/home.html')