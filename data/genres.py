import sqlalchemy.orm as orm
import datetime
import sqlalchemy
from sqlalchemy import *
from werkzeug.security import *

from .db_session import SqlAlchemyBase


class Genre(SqlAlchemyBase):
    __tablename__ = 'genres'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True)
