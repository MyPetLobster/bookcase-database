from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash   
from .models import Book, Bookcase, User
from . import db
from sqlalchemy.exc import IntegrityError
import urllib.request, json
import os
from urllib.parse import urlencode


views = Blueprint('views', __name__)


# HOME PAGE
@views.route('/')
@views.route('/home/')
def home():
    return render_template("home.html", user=current_user)

# PROFILE 
@views.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.username if current_user.is_authenticated else None
    bookcases = Bookcase.query.filter_by(owner_id=current_user.id).all()
    total_books = current_user.total_book_count()
    return render_template("profile.html", username=username, user=current_user, bookcases=bookcases, total_books=total_books)

# BOOKCASES 
@views.route('/bookcases/', methods=['GET', 'POST'])
@login_required
def bookcases():
    # Fetch the bookcases associated with the current user
    bookcases = Bookcase.query.filter_by(owner_id=current_user.id).all()
    if request.method == 'POST':
        name = request.form.get('bookcase-name')
        owner_id = current_user.id
        new_bookcase = Bookcase(name=name, owner_id=owner_id)
        # Check if the bookcase already exists, if so alert error
        if Bookcase.query.filter_by(name=name, owner_id=owner_id).first():
            flash('Bookcase already exists!', category='error')
            return render_template("bookcases.html", user=current_user, bookcases=bookcases)
        db.session.add(new_bookcase)
        db.session.commit()
        return redirect(url_for('views.bookcases'))
        
    return render_template("bookcases.html", user=current_user, bookcases=bookcases)

# BOOKCASE DETAILS 
@views.route('/bookcase/<int:id>/', methods=['GET', 'POST'])
@login_required
def bookcase(id):
    current_bookcase=Bookcase.query.get(id)
    if request.method == 'POST':
        
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        authors = request.form.get('authors')
        description = request.form.get('description')
        description_truncated = ""
        categories = request.form.get('categories')
        publisher = request.form.get('publisher')
        publication_date = request.form.get('publication_date')
        isbn_13 = request.form.get('isbn_13')
        isbn_10 = request.form.get('isbn_10')
        language = request.form.get('language')
        pages = request.form.get('pages')
        thumbnail_link = request.form.get('thumbnail_link')
        user_notes = request.form.get('user_notes')
        user_rating = request.form.get('user_rating')
        read = request.form.get('read')
        if (read == "true"):
            read = True
        elif (read == "false"):
            read = False
        # Convert the 'on' or 'off' string to a boolean
        read_value = read == 'on'

        # Create truncated description
        if description != None:
            if len(description) > 150:
                description_truncated = description[:150] + "..."
        try:
            new_book = Book(
                title=title,
                subtitle=subtitle,
                authors=authors,
                description=description,
                description_truncated=description_truncated,
                categories=categories,
                publisher=publisher,
                publication_date=publication_date,
                isbn_13=isbn_13,
                isbn_10=isbn_10,
                language=language,
                pages=pages,
                thumbnail_link=thumbnail_link,
                user_rating=user_rating,
                user_notes=user_notes,
                read=read_value
            )     

            current_bookcase.books.append(new_book)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("IntegrityError: The book may already exist.")

    # Check if the user owns the bookcase before allowing them to view it
    if current_bookcase.owner_id != current_user.id:
        return redirect(url_for('views.bookcases'))
    return render_template("bookcase.html", id=id, current_bookcase=current_bookcase, user=current_user)

# BOOK DETAILS
@views.route('/bookcase/<int:bc_id>/<int:book_id>/')
@login_required
def book(bc_id, book_id):
    current_bookcase = Bookcase.query.get(bc_id)
    book = Book.query.get(book_id)
    return render_template("book.html", current_bookcase=current_bookcase, user=current_user, book=book)

# SEARCH PAGE
@views.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    bookcases = Bookcase.query.filter_by(owner_id=current_user.id).all()
    if request.method == 'POST':
        
        # check if user creates new bookcase
        if request.form.get('bookcase-name'):
            name = request.form.get('bookcase-name')
            owner_id = current_user.id
            new_bookcase = Bookcase(name=name, owner_id=owner_id)
            db.session.add(new_bookcase)
            db.session.commit()
            # refresh page
            return redirect(url_for('views.search'))
        
        # Check if user submits the search form which includes author, title and isbn fields
        elif request.form.get('author') or request.form.get('title') or request.form.get('isbn'):
            author = ''
            title = ''
            isbn = ''
            q_string = ''

            if request.form.get('author'):
                author = request.form.get('author')
                # separate author into list of strings
                author = author.split()
                # join the list of strings into a string with "+" between each word
                author = "+".join(author)
                q_string = f"inauthor:{author}"

            if request.form.get('title'):
                title = request.form.get('title')
                # separate title into list of strings
                title = title.split()
                # join the list of strings into a string with "+" between each word
                title = "+".join(title)
                q_string += f"+intitle:{title}"

            if request.form.get('isbn'):
                isbn = request.form.get('isbn')
                q_string += f"+isbn:{isbn}"

            api_key = os.environ.get('GOOGLE_BOOKS_API_KEY')
            
            query_params = {
                'q': q_string,
                'key': api_key,
            }
            
            url = f"https://www.googleapis.com/books/v1/volumes?{urlencode(query_params)}"
            session['search_query'] = url
            
            data = urllib.request.urlopen(url).read()
            dict = json.loads(data)

            return render_template("search.html", user=current_user, books=dict['items'], bookcases=bookcases)

        elif request.form.get('general-search'):
            general_search = request.form.get('general-search')
            general_search = general_search.split()
            general_search = "+".join(general_search)
            api_key = os.environ.get('GOOGLE_BOOKS_API_KEY')
            query_params = {
                'q': general_search,
                'key': api_key,
            }
            url = f"https://www.googleapis.com/books/v1/volumes?{urlencode(query_params)}"
            session['search_query'] = url
            data = urllib.request.urlopen(url).read()
            dict = json.loads(data)
            return render_template("search.html", user=current_user, books=dict['items'], bookcases=bookcases)

        else:
            # Handle integrity error (e.g., if the book already exists)
            db.session.rollback()
            print("IntegrityError: The book may already exist.")
            

    return render_template("search.html", user=current_user, bookcases=bookcases)




def add_book(template_string):
    bookcases = Bookcase.query.filter_by(owner_id=current_user.id).all()

    # Which bookcase did user select?
    if request.form.get('bookcase'):
        bookcase_id = request.form.get('bookcase')
        current_bookcase = Bookcase.query.get(bookcase_id)

    # Retrieve all form data
    title = request.form.get('book-title')
    subtitle = request.form.get('book-subtitle')
    authors = request.form.get('book-author')
    description = request.form.get('book-description')
    description_truncated = ""
    if description != None:
        if len(description) > 150:
            description_truncated = description[:150] + "..."
    categories = request.form.get('book-categories')
    publisher = request.form.get('book-publisher')
    publication_date = request.form.get('book-publication-date')
    isbn_13 = request.form.get('book-isbn-13')
    isbn_10 = request.form.get('book-isbn-10')
    language = request.form.get('book-language')
    pages = request.form.get('book-pages')
    google_books_rating = request.form.get('book-google-rating')
    # check type of google_books_rating
    if type(google_books_rating) == str:
        google_books_rating = float(0)
    google_books_rating_count = request.form.get('book-google-books-count')
    thumbnail_link = request.form.get('book-thumbnail-link')
    google_books_link = request.form.get('book-google-books-link')
    google_books_id = request.form.get('book-google-books-id')

    # Check if the current bookcase exists and belongs to the current user
    if current_bookcase and current_bookcase.owner_id == current_user.id:
        try:
            # Create a new book
            new_book = Book(
                title=title, 
                subtitle=subtitle, 
                authors=authors, 
                description=description, 
                description_truncated=description_truncated,
                categories=categories,
                publisher=publisher, 
                publication_date=publication_date, 
                isbn_13=isbn_13, 
                isbn_10=isbn_10,
                language=language, 
                pages=pages, 
                google_books_rating=google_books_rating,
                google_books_rating_count=google_books_rating_count, 
                thumbnail_link=thumbnail_link,
                google_books_link=google_books_link, 
                google_books_id=google_books_id
            )
            
            # Add the book to the current bookcase
            current_bookcase.books.append(new_book)
            
            # Commit changes to the database
            db.session.commit()
        
        except IntegrityError:
            # Handle integrity error (e.g., if the book already exists)
            db.session.rollback()
            print("IntegrityError: The book may already exist.")

    url = session.get('search_query')
    data = urllib.request.urlopen(url).read()
    dict = json.loads(data)
    if (template_string == "search.html"):
        return render_template(template_string, user=current_user, books=dict['items'], bookcases=bookcases)
    # Check if template_string starts with "bookcase"
    elif (template_string[:8] == "bookcase"):
        return render_template(template_string, id=current_bookcase.id, current_bookcase=current_bookcase, user=current_user)
    
    







# ADD BOOK TO BOOKCASE
@views.route('/search/add_book/', methods=['POST'])
@login_required
def add_book():
    bookcases = Bookcase.query.filter_by(owner_id=current_user.id).all()

    # Which bookcase did user select?
    if request.form.get('bookcase'):
        bookcase_id = request.form.get('bookcase')
        current_bookcase = Bookcase.query.get(bookcase_id)

    # Retrieve all form data
    title = request.form.get('book-title')
    subtitle = request.form.get('book-subtitle')
    authors = request.form.get('book-author')
    description = request.form.get('book-description')
    description_truncated = ""
    if description != None:
        if len(description) > 150:
            description_truncated = description[:150] + "..."
    categories = request.form.get('book-categories')
    publisher = request.form.get('book-publisher')
    publication_date = request.form.get('book-publication-date')
    isbn_13 = request.form.get('book-isbn-13')
    isbn_10 = request.form.get('book-isbn-10')
    language = request.form.get('book-language')
    pages = request.form.get('book-pages')
    google_books_rating = request.form.get('book-google-rating')
    # check type of google_books_rating
    if type(google_books_rating) == str:
        google_books_rating = float(0)
    google_books_rating_count = request.form.get('book-google-books-count')
    thumbnail_link = request.form.get('book-thumbnail-link')
    google_books_link = request.form.get('book-google-books-link')
    google_books_id = request.form.get('book-google-books-id')

    # Check if the current bookcase exists and belongs to the current user
    if current_bookcase and current_bookcase.owner_id == current_user.id:
        try:
            # Create a new book
            new_book = Book(
                title=title, 
                subtitle=subtitle, 
                authors=authors, 
                description=description, 
                description_truncated=description_truncated,
                categories=categories,
                publisher=publisher, 
                publication_date=publication_date, 
                isbn_13=isbn_13, 
                isbn_10=isbn_10,
                language=language, 
                pages=pages, 
                google_books_rating=google_books_rating,
                google_books_rating_count=google_books_rating_count, 
                thumbnail_link=thumbnail_link,
                google_books_link=google_books_link, 
                google_books_id=google_books_id
            )
            
            # Add the book to the current bookcase
            current_bookcase.books.append(new_book)
            
            # Commit changes to the database
            db.session.commit()
        
        except IntegrityError:
            # Handle integrity error (e.g., if the book already exists)
            db.session.rollback()
            print("IntegrityError: The book may already exist.")

    url = session.get('search_query')
    data = urllib.request.urlopen(url).read()
    dict = json.loads(data)
    return render_template("search.html", user=current_user, books=dict['items'], bookcases=bookcases)
    
# DELETE BOOK FROM BOOKCASE
@views.route('/bookcase/<int:bc_id>/<int:book_id>/delete_book/', methods=['GET', 'POST'])
@login_required
def delete_book(bc_id, book_id):
    current_bookcase = Bookcase.query.get(bc_id)
    book = Book.query.get(book_id)
    if current_bookcase and current_bookcase.owner_id == current_user.id:
        try:
            current_bookcase.books.remove(book)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("IntegrityError: The book may already exist.")
    return redirect(url_for('views.bookcase', id=bc_id))

# EDIT BOOK DETAILS
@views.route('/bookcase/<int:bc_id>/<int:book_id>/edit_book/', methods=['GET', 'POST'])
@login_required
def edit_book(bc_id, book_id):
    current_bookcase = Bookcase.query.get(bc_id)
    book = Book.query.get(book_id)

    # Retrieve all book data
    title = book.title
    subtitle = book.subtitle
    authors = book.authors
    description = book.description
    categories = book.categories
    publisher = book.publisher
    publication_date = book.publication_date
    isbn_13 = book.isbn_13
    isbn_10 = book.isbn_10
    language = book.language
    pages = book.pages
    user_rating = book.user_rating
    user_notes = book.user_notes
    read = book.read

    print(f"user rating: {user_rating}")
    print("-------------------")
    
    if request.method == 'POST' and current_bookcase and current_bookcase.owner_id == current_user.id:

        try:
            # Retrieve all form data
            title = request.form.get('book-title') 
            subtitle = request.form.get('book-subtitle')
            authors = request.form.get('book-authors')
            description = request.form.get('book-description')
            categories = request.form.get('book-categories')
            publisher = request.form.get('book-publisher')
            publication_date = request.form.get('book-publication-date')
            isbn_13 = request.form.get('book-isbn-13')
            isbn_10 = request.form.get('book-isbn-10')
            language = request.form.get('book-language')
            pages = request.form.get('book-pages')
            user_rating = request.form.get('book-user-rating')
            user_notes = request.form.get('book-user-notes')
            read = request.form.get('book-read')
            if (read == "true"):
                read = True
            elif (read == "false"):
                read = False
            # Convert the 'on' or 'off' string to a boolean
            read_value = read == 'on'
        
            # Create truncated description
            if len(description) > 150:
                description_truncated = description[:150] + "..."

            # Update the book
            book.title = title
            book.subtitle = subtitle
            book.authors = authors
            book.description = description
            book.description_truncated = description_truncated
            book.categories = categories
            book.publisher = publisher
            book.publication_date = publication_date
            book.isbn_13 = isbn_13
            book.isbn_10 = isbn_10
            book.language = language
            book.pages = pages
            book.user_rating = user_rating
            book.user_notes = user_notes
            book.read = read_value
            book.user_notes = user_notes
            book.read = read


            

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("IntegrityError: The book may already exist.")

        return redirect(url_for('views.book', bc_id=bc_id, book_id=book_id))
    
    return render_template("edit_book.html", current_bookcase=current_bookcase, user=current_user, book=book)

# EDIT USER PROFILE
@views.route("/edit_profile/", methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Retrieve all form data
        username = request.form.get('edit-username')
        email = request.form.get('edit-email')
        emailConfirm = request.form.get('edit-email-confirm')
        password = request.form.get('edit-password')
        passwordConfirm = request.form.get('edit-password-confirm')

        if password != passwordConfirm:
            flash('Passwords do not match!', category='error')
            return render_template("edit_profile.html", user=current_user)
        if email != emailConfirm:
            flash('Emails do not match!', category='error')
            return render_template("edit_profile.html", user=current_user)

        # Update the user
        current_user.username = username
        current_user.email = email
        current_user.password = generate_password_hash(password, method='pbkdf2:sha256')

        db.session.commit()

        return redirect(url_for('views.profile'))

    return render_template("edit_profile.html", user=current_user)

# DELETE USER PROFILE
@views.route("/delete_profile/", methods=['GET', 'POST'])
@login_required
def delete_profile():
    if request.method == 'POST':
        # Retrieve all form data
        password = request.form.get('delete-password')
        passwordConfirm = request.form.get('delete-password-confirm')

        if password != passwordConfirm:
            flash('Passwords do not match!', category='error')
            return render_template("edit_profile.html", user=current_user)

        if not check_password_hash(current_user.password, password):
            flash('Incorrect password!', category='error')
            return render_template("edit_profile.html", user=current_user)

        # Delete the user
        db.session.delete(current_user)
        db.session.commit()

        return redirect(url_for('views.home'))

    return render_template("edit_profile.html", user=current_user)

# ABOUT PAGE
@views.route('/about/')
def about():
    return render_template("about.html", user=current_user)
