import sqlalchemy.orm as orm
import datetime
import sqlalchemy
from flask_login import *
from sqlalchemy import *
from werkzeug.security import *

from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase, UserMixin):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    genre_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("genres.id"))
    author = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True)
    for_class = sqlalchemy.Column(sqlalchemy.String)
    avatar = sqlalchemy.Column(sqlalchemy.String, default='listt.png')
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    about = sqlalchemy.Column(sqlalchemy.String)
    story_of_creation = sqlalchemy.Column(sqlalchemy.String)
    biography = sqlalchemy.Column(sqlalchemy.String)
    comments = orm.relationship("Comment", back_populates='book')
    genre = orm.relationship('Genre')
