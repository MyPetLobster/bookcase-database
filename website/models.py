from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func

# Association Table
bookcases = db.Table('bookcases',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('bookcase_id', db.Integer, db.ForeignKey('bookcase.id')),
    db.ForeignKeyConstraint(['user_id', 'bookcase_id'], ['bookcases.user_id', 'bookcases.bookcase_id'])
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    bookcases = db.relationship('Bookcase', backref='owner', secondary=bookcases,
                                primaryjoin=('User.id == bookcases.c.user_id'),
                                secondaryjoin=('and_(User.id == bookcases.c.user_id, Bookcase.id == bookcases.c.bookcase_id)'),
                                lazy='dynamic')

class Bookcase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    books = db.relationship('Book', secondary=bookcases, backref=db.backref('bookcases', lazy='dynamic'))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(150))
    genre = db.Column(db.String(150))
