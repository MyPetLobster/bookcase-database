from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

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

class Bookcase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Define the many-to-many relationship
    books = db.relationship('Book', secondary=bookcase_book_association, back_populates='bookcases')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(150))
    isbn = db.Column(db.String(150))
    year = db.Column(db.String(150))
    pages = db.Column(db.String(150))
    user_rating = db.Column(db.String(150))
    goodreads_rating = db.Column(db.String(150))    
    genre = db.Column(db.String(150))
    
    # Define the back-reference in Book model
    bookcases = db.relationship('Bookcase', secondary=bookcase_book_association, back_populates='books')
