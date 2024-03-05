import bcrypt
from flask_login import UserMixin
from sqlalchemy.orm import reconstructor

from db import db
from models.password import Password


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    __password_column = db.Column(db.String(72), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    def __init__(self, email, password, role):
        self.email = email
        self.__password = Password.from_plaintext(password)
        self.__password_column = self.__password.hash
        self.role = role

    @reconstructor
    def init_on_load(self):
        self.__password = Password.from_hash(self.__password_column)

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password: str):
        self.__password = Password.from_plaintext(password)
        self.__password_column = self.__password.hash
