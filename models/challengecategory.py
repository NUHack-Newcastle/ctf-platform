import os
import json
from typing import Set

from models.challenge import Challenge


class ChallengeCategory:
    def __init__(self, slug: str, name: str):
        self.__slug: str = slug
        self.__name: str = name
        self.__challenges: Set[Challenge] = set()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def slug(self) -> str:
        return self.__slug

    @property
    def challenges(self) -> Set[Challenge]:
        return self.__challenges.copy()

    def add_challenge(self, challenge: Challenge):
        self.__challenges.add(challenge)

    @staticmethod
    def from_directory(directory: str) -> 'ChallengeCategory':
        if not os.path.isdir(directory) or not os.path.exists(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read()
        f.close()

        return ChallengeCategory(slug=os.path.split(directory)[-1], name=name)
