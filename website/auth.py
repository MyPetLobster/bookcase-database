from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash   


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print(request.form)
        print(f"rfg(username) = {request.form.get('username')}")

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('psw')
        password2 = request.form.get('psw-repeat')

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
        
    return render_template("register.html")


@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('psw')

        user = User.query.filter_by(username=username).first()

        if user: 
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')  

    return render_template("login.html")



@auth.route('/logout')  
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))






# def login():
#     if request.method == 'POST':
#         username = request.form.get('usrname')
#         password = request.form.get('psw')
#         remember = True if request.form.get('remember') else False

#         user = User.query.filter_by(username=username).first()

#         if not user or not check_password_hash(user.password, password):
#             flash('Please check your login details and try again.', category='error')
#         else:
#             login_user(user, remember=remember)
#             flash('Logged in successfully!', category='success')
#             return redirect(url_for('views.home'))
    
#     return render_template("login.html")
