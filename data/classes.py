import sqlalchemy.orm as orm
import datetime
import sqlalchemy
from flask_login import *
from sqlalchemy import *
from werkzeug.security import *

from .db_session import SqlAlchemyBase


class Class(SqlAlchemyBase, UserMixin):
    __tablename__ = 'classes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    code_class = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True)
    students = sqlalchemy.Column(sqlalchemy.String, nullable=True)


    avatar = sqlalchemy.Column(sqlalchemy.String, default='avatar0.jpeg')
    registration_date = sqlalchemy.Column(sqlalchemy.Date, default=datetime.date.today)

    class_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
