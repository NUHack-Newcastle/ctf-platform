from db import db
from slugify import slugify


class Team(db.Model):
    __slug_column = db.Column(db.String(64), nullable=False, unique=True, primary_key=True)
    __name_column = db.Column(db.String(64), nullable=False, unique=True)

    def __init__(self, name: str):
        self.__name_column = name
        self.__slug_column = slugify(name)

    @property
    def name(self) -> str:
        return self.__name_column

    @property
    def slug(self) -> str:
        return self.__slug_column
