from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from . import mail
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import os
import secrets
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


auth = Blueprint('auth', __name__)


# REGISTER
@auth.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print(request.form)
        print(f"rfg(username) = {request.form.get('username')}")

        username = request.form.get('username').strip()
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password-confirm')

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        print(f'{email}, {username}, {password}, {password2}')
        print("**************************")

        if email_exists:
            flash('Email already exists.', category='error')
        elif username_exists:
            flash('Username already exists.', category='error')
        elif password != password2:
            flash('Passwords do not match.', category='error')
        elif len(username) < 3:
            flash('Username must be at least 3 characters.', category='error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', category='error')
        elif password != password2:
            flash('Passwords do not match.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            # add the variable that stores the new user (User object) to the database
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("register.html", user=current_user)

# LOGIN
@auth.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('psw')
        remember = request.form.get('remember')
        if (remember == 'on'):
            remember = True
        else:
            remember = False

        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=remember)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("login.html", user=current_user)

# LOGOUT
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


# FORGOT PASSWORD
secret_key = os.environ.get('SECRET_TOKEN', secrets.token_hex(32))
def generate_reset_token(user_id):
    s = URLSafeTimedSerializer(secret_key)
    return s.dumps({'user_id': user_id})


@auth.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':

        input = request.form.get('email-username')
        # check if input is an email address or username
        if '@' in input:
            email = input
            user = User.query.filter_by(email=email).first()
        else:
            username = input
            user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
            email = user.email

        if user:
            user.reset_token = generate_reset_token(user.id)
            db.session.commit()

            msg = Message(subject='Bookcase Database Password Reset', sender='BookcaseDatabase@gmail.com', recipients=[email])
            msg.body = f"Hello {user.username},\n\nYou recently requested to reset your password for your Bookcase Database account. Click the link below to reset it.\n\nhttps://mypetlobster.pythonanywhere.com/reset_password/{user.id}/{user.reset_token}\n\nIf you did not request a password reset, please ignore this email.\n\nThanks,\nBookcase Database"
            mail.send(msg)
    return render_template("forgot_password.html", user=current_user)


# RESET PASSWORD
@auth.route('/reset_password/<int:user_id>/<token>/', methods=['GET', 'POST'])
def reset_password(user_id, token):
    if request.method == 'POST':
        s = URLSafeTimedSerializer(secret_key)
        try:
            data = s.loads(token, max_age=1800)
            if data.get('user_id') == user_id:
                password = request.form.get('password')
                password_confirm = request.form.get('password-confirm')
                if password != password_confirm:
                    flash('Passwords do not match!', category='error')
                    return render_template("reset_password.html", user=current_user)
                user = User.query.get(user_id)
                user.password = generate_password_hash(password, method='pbkdf2:sha256')
                db.session.commit()
                return redirect(url_for('auth.login'))
            else:
                flash('The token is invalid!', category='error')
        except SignatureExpired:
            flash('The token is expired!', category='error')
        except BadSignature:
            flash('The token is invalid!', category='error')

    return render_template("reset_password.html", user_id=user_id, user=current_user, token=token)




