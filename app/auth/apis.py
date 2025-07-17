from flask import render_template,redirect,request,flash,url_for
from flask_login import current_user,login_required,login_user,logout_user
from app.auth.forms import LoginForm, RegisterForm
from app.models import User
from app import db
from app.auth import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('You are loged in. ')   
            return redirect('/chat/chat')     

    return render_template('auth/login.html',form=form)

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