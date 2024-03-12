from db import db
from slugify import slugify


class Team(db.Model):
    __slug_column = db.Column('slug', db.String(64), nullable=False, unique=True, primary_key=True)
    __name_column = db.Column('name', db.String(64), nullable=False, unique=True)
    users = db.relationship('User', backref='_User__team')

    def __init__(self, name: str):
        self.__name_column = name
        self.__slug_column = slugify(name)

    @property
    def name(self) -> str:
        return self.__name_column

    @property
    def slug(self) -> str:
        return self.__slug_column

    @property
    def any_pending(self) -> bool:
        return any(u.team_pending for u in self.users)
