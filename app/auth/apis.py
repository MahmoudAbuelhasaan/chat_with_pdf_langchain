from flask import render_template,redirect,request,flash,url_for
from flask_login import current_user,login_required
from app.auth.forms import LoginForm, RegisterForm
from app.models import User
from app import db
from app.auth import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():

    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User(username=username,email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('You are registered')
        return redirect('/auth/login')
        
    return render_template('auth/register.html',form=form)

def logout():
    pass