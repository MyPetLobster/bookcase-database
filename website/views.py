from flask import Blueprint, render_template
from flask_login import current_user, login_required

views = Blueprint('views', __name__)

##### LOGIN REQUIRED #####
@views.route('/')
@views.route('/home/')
@views.route('/search/')
@login_required
def home():
    return render_template("home.html")

@views.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.username if current_user.is_authenticated else None
    return render_template("profile.html", username=username)

@views.route('/bookcases/')
@login_required
def bookcases():
    return render_template("bookcases.html")

@views.route('/bookcase/<int:id>/')
@login_required
def bookcase(id):
    return render_template("bookcase.html", id=id)

@views.route('/book/<int:id>/')
@login_required
def book(id):
    return render_template("book.html", id=id)




##### NO LOGIN REQUIRED #####
@views.route('/signup/')
def signup():
    return render_template("signup.html")

@views.route('/login/')
def login():
    return render_template("login.html")    

@views.route('/about/')
def about():
    return render_template("about.html")
