from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, date

# Intermediate table to represent the many-to-many relationship
bookcase_book_association = db.Table(
    'bookcase_book_association',
    db.Column('bookcase_id', db.Integer, db.ForeignKey('bookcase.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    reset_token = db.Column(db.String(120), nullable=True)
    def total_book_count(self):
        # Use a query to count the total number of books associated with the user
        total_count = (
            db.session.query(func.count(Book.id))
            .join(bookcase_book_association)
            .join(Bookcase)
            .filter(Bookcase.owner_id == self.id)
            .scalar()
        )
        return total_count

class Bookcase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Define the many-to-many relationship
    books = db.relationship('Book', secondary=bookcase_book_association, back_populates='bookcases')


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)        # primary key, hidden from user, Tier 5
    title = db.Column(db.String(150))                   # from google books api, Tier 1
    subtitle = db.Column(db.String(150))                # from google books api, Tier 2
    authors = db.Column(db.JSON)                        # from google books api, Tier 1
    description = db.Column(db.String(1500))            # from google books api, Tier 2
    description_truncated = db.Column(db.String(150))   # from google books api, Tier 2
    categories = db.Column(db.JSON)                     # from google books api, Tier 2
    publisher = db.Column(db.String(150))               # from google books api, Tier 2
    publication_date = db.Column(db.String(150))        # from google books api, Tier 2
    isbn_13 = db.Column(db.String(150))                 # from google books api, Tier 3
    isbn_10 = db.Column(db.String(150))                 # from google books api, Tier 3      
    language = db.Column(db.String(150))                # from google books api, Tier 3
    pages = db.Column(db.Integer)                       # from google books api, Tier 3
    google_books_rating = db.Column(db.Numeric(2, 1))   # from google books api, Tier 4
    google_books_rating_count = db.Column(db.Integer)   # from google books api, Tier 1 
    thumbnail_link = db.Column(db.String(150))          # from google books api, Tier 3
    google_books_link = db.Column(db.String(150))       # from google books api, Tier 3
    google_books_id = db.Column(db.String(150))         # from google books api, hidden from user, Tier 5
    user_rating = db.Column(db.Numeric(2, 1))           # from user, Tier 1
    read = db.Column(db.Boolean, default=False)         # from user, Tier 1
    user_notes = db.Column(db.String(1500))             # from user, Tier 2
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) # from user, hidden from user, Tier 5
    # Define the back-reference in Book model
    bookcases = db.relationship('Bookcase', secondary=bookcase_book_association, back_populates='books')
