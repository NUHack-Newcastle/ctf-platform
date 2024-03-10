import os
import json
from typing import Optional


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
        if not os.path.isdir(directory) or not os.path.exists(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read()
        f.close()

        return Challenge(slug=os.path.split(directory)[-1], name=name, category=category)
