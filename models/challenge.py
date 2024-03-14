import os
import json
from typing import Optional, Set

from flask_login import current_user

from db import db
from models.solve import Solve


class Challenge:
    def __init__(self, slug: str, name: str, category: Optional['ChallengeCategory'] = None):
        self.__slug: str = slug
        self.__name: str = name
        self.__category: Optional['ChallengeCategory'] = category

    @property
    def name(self) -> str:
        return self.__name

    @property
    def slug(self) -> str:
        return self.__slug

    @property
    def category(self) -> Optional['ChallengeCategory']:
        return self.__category

    @staticmethod
    def from_directory(directory: str, category=None) -> 'Challenge':
        if not os.path.isdir(directory) or not os.path.isfile(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read()
        f.close()

        return Challenge(slug=os.path.split(directory)[-1], name=name, category=category)

    @property
    def solves(self) -> Set['Solve']:
        # not sure the proper way to do this in sqlalchemy! hybrid properties didn't seem to work!
        return set(s for s in Solve.query.all() if s.challenge == self)
