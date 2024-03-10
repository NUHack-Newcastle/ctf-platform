import os
import json
import sys
from typing import Set
from models.challenge import Challenge
from models.challengecategory import ChallengeCategory
from models.flag_manager import FlagManager


class Event:
    def __init__(self, name: str, categories: Set[ChallengeCategory]):
        self.__name: str = name
        self.__categories: Set[ChallengeCategory] = categories
        self.__flag_manager: FlagManager = FlagManager(self)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def categories(self) -> Set[ChallengeCategory]:
        return self.__categories

    @property
    def challenges(self) -> Set[Challenge]:
        return set().union(*(c.challenges for c in self.categories))

    @property
    def flag_manager(self) -> FlagManager:
        return self.__flag_manager

    @property
    def secret_key(self) -> str:
        # todo: implement per-event secret
        return "super secret key"

    @staticmethod
    def from_directory(directory: str) -> 'Event':
        if not os.path.isdir(directory) or not os.path.exists(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read()
        f.close()

        categories: Set[ChallengeCategory] = set()
        challenges: Set[Challenge] = set()
        if os.path.isdir(os.path.join(directory, 'challenges')):
            for category_slug in os.listdir(os.path.join(directory, 'challenges')):
                if not os.path.isdir(os.path.join(directory, 'challenges', category_slug)):
                    continue
                category = ChallengeCategory.from_directory(os.path.join(directory, 'challenges', category_slug))
                assert not any(category.slug == c.slug for c in categories)
                categories.add(category)
                for challenge_slug in os.listdir(os.path.join(directory, 'challenges', category_slug)):
                    if not os.path.isdir(os.path.join(directory, 'challenges', category_slug, challenge_slug)):
                        continue
                    challenge = Challenge.from_directory(os.path.join(directory, 'challenges', category_slug, challenge_slug), category=category)
                    assert not any(challenge.slug == c.slug for c in challenges)
                    category.add_challenge(challenge)
                    challenges.add(challenge)
        else:
            sys.stderr.write("Warning: could not find challenges directory\n")

        return Event(name, categories)
