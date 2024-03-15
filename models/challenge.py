import os
import json
import sys
from typing import Optional, Set

from flask_login import current_user

from db import db
from models.solve import Solve


class Challenge:
    def __init__(self, slug: str, name: str, category: Optional['ChallengeCategory'] = None, difficulty: Optional[int] = None):
        self.__slug: str = slug
        self.__name: str = name
        self.__category: Optional['ChallengeCategory'] = category
        self.__difficulty: Optional[int] = difficulty

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

        difficulty: Optional[int] = None
        if os.path.isfile(os.path.join(directory, 'difficulty')):
            f = open(os.path.join(directory, 'splash_border'), 'r')
            try:
                difficulty = int(f.read())
                if difficulty > 5 or difficulty < 0:
                    sys.stderr.write(f"Cannot load difficulty for challenge {name}, must be between 0-5. Setting as None")
            except ValueError:
                sys.stderr.write(f"Cannot load difficulty for challenge {name}, it is not an int. Setting as None")
            f.close()

        return Challenge(slug=os.path.split(directory)[-1], name=name, category=category, difficulty=difficulty)

    @property
    def difficulty(self) -> Optional[int]:
        return self.__difficulty

    @property
    def solves(self) -> Set['Solve']:
        # not sure the proper way to do this in sqlalchemy! hybrid properties didn't seem to work!
        return set(s for s in Solve.query.all() if s.challenge == self)

    @property
    def base_points(self) -> int:
        if self.difficulty is None or self.difficulty > 5 or self.difficulty < 0:
            # default 500 points
            return 500
        elif self.difficulty == 0:
            # only for example challenges
            return 100
        elif self.difficulty == 1:
            return 500
        elif self.difficulty == 2:
            return 1000
        elif self.difficulty == 3:
            return 2500
        elif self.difficulty == 4:
            return 3500
        elif self.difficulty == 5:
            return 5000

    @property
    def allow_multiplier(self) -> bool:
        # allow multiplier for all except example challenges
        return self.difficulty != 0
