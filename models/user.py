import copy
import json

import bcrypt
import requests
from flask_login import UserMixin
from sqlalchemy.orm import reconstructor
import sqlalchemy
from werkzeug.exceptions import BadRequest

from db import db
from models.avatar import Avatar
from models.password import Password


class User(db.Model, UserMixin):
    username = db.Column(db.String(32), primary_key=True, nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    __password_column = db.Column('password', db.String(72), nullable=False)
    __role_column = db.Column('role', db.String(100), nullable=False, default='user')
    __avatar_style = db.Column('avatar_style', db.String(64), nullable=False)
    __avatar_seed = db.Column('avatar_seed', db.String(64), nullable=False)
    __avatar_options = db.Column('avatar_options', db.String(1024), nullable=False)

    def __init__(self, username, email, password, role, avatar_style: str, avatar_seed: str, avatar_options: dict):
        self.username = username
        self.email = email
        self.__password = Password.from_plaintext(password)
        self.__password_column = self.__password.hash
        self.__role_column = role
        self.__avatar: Avatar = Avatar(avatar_style, avatar_seed, avatar_options)
        self.__avatar_style = avatar_style
        self.__avatar_seed = avatar_seed
        self.__avatar_options = json.dumps(avatar_options)

    def get_id(self):
        return self.username

    @reconstructor
    def init_on_load(self):
        self.__password = Password.from_hash(self.__password_column)
        self.__avatar: Avatar = Avatar(self.__avatar_style, self.__avatar_seed, json.loads(self.__avatar_options))

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password: str):
        self.__password = Password.from_plaintext(password)
        self.__password_column = self.__password.hash

    @property
    def avatar(self):
        return self.__avatar

    @avatar.setter
    def avatar(self, avatar: Avatar):
        self.__avatar = avatar
        self.__update_avatar()

    def edit_avatar(self, style: str, seed:str, options: dict):
        new_avatar = Avatar(style, seed, options)
        if not requests.get(str(new_avatar)).ok:
            raise BadRequest
        self.avatar = new_avatar
        self.__update_avatar()

    def __update_avatar(self):
        self.__avatar_style = self.avatar.style
        self.__avatar_seed = self.avatar.seed
        self.__avatar_options = json.dumps(dict(self.avatar.options) | dict(self.avatar.customisations))

    @property
    def is_admin(self):
        return self.__role_column == 'admin'

    def __str__(self):
        return self.username
