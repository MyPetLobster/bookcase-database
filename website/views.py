from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import Book, Bookcase, User
from . import db
from sqlalchemy.exc import IntegrityError

views = Blueprint('views', __name__)

##### LOGIN REQUIRED #####
@views.route('/')
@views.route('/home/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.username if current_user.is_authenticated else None
    return render_template("profile.html", username=username, user=current_user)

@views.route('/bookcases/', methods=['GET', 'POST'])
@login_required
def bookcases():
    # Fetch the bookcases associated with the current user
    bookcases = Bookcase.query.filter_by(owner_id=current_user.id).all()
    if request.method == 'POST':
        name = request.form.get('bookcase-name')
        owner_id = current_user.id
        new_bookcase = Bookcase(name=name, owner_id=owner_id)
        db.session.add(new_bookcase)
        db.session.commit()
        
    return render_template("bookcases.html", user=current_user, bookcases=bookcases)

@views.route('/bookcase/<int:id>/', methods=['GET', 'POST'])
@login_required
def bookcase(id):
    if request.method == 'POST':
        # Retrieve form data
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn') 
        year = request.form.get('year')
        pages = request.form.get('pages')
        user_rating = request.form.get('user-rating')
        goodreads_rating = request.form.get('goodreads-rating')
        genre = request.form.get('genre')

        # Get the current bookcase
        current_bookcase = Bookcase.query.get(id)

        # Check if the current bookcase exists and belongs to the current user
        if current_bookcase and current_bookcase.owner_id == current_user.id:
            try:
                # Create a new book
                new_book = Book(
                    title=title, author=author, isbn=isbn, year=year, pages=pages,
                    user_rating=user_rating, goodreads_rating=goodreads_rating, genre=genre
                )
                
                # Add the book to the current bookcase
                current_bookcase.books.append(new_book)
                
                # Commit changes to the database
                db.session.commit()

                return redirect(url_for('views.bookcase', id=id))
            
            except IntegrityError:
                # Handle integrity error (e.g., if the book already exists)
                db.session.rollback()
                print("IntegrityError: The book may already exist.")

        # Fetch the books associated with the current bookcase
        current_bookcase_name = current_bookcase.name
        return render_template("bookcase.html", id=id, bookcase_name=current_bookcase_name, user=current_user, book=new_book)

    current_bookcase=Bookcase.query.get(id)
    return render_template("bookcase.html", id=id, current_bookcase=current_bookcase, user=current_user)


@views.route('/book/<int:id>/')
@login_required
def book(id):
    return render_template("book.html", id=id, user=current_user)



##### SEARCH PAGE #####
@views.route('/search/', methods=['GET', 'POST'])
@login_required
def search_home():
    return render_template("search.html", user=current_user)

@views.route('/search/<string:query>/', methods=['GET', 'POST'])
@login_required
def search(query):
    return render_template("search.html", query=query, user=current_user)


##### NO LOGIN REQUIRED #####
@views.route('/about/')
def about():
    return render_template("about.html", user=current_user)
