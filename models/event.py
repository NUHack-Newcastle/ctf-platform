import os
import json
import sys
from typing import Set, Optional
from models.challenge import Challenge
from models.challengecategory import ChallengeCategory
from models.flag_manager import FlagManager


class Event:
    def __init__(self, name: str, categories: Set[ChallengeCategory], logo: Optional[bytes] = None):
        self.__name: str = name
        self.__categories: Set[ChallengeCategory] = categories
        self.__flag_manager: FlagManager = FlagManager(self)
        self.__logo: Optional[bytes] = logo

    @property
    def name(self) -> str:
        return self.__name

    @property
    def categories(self) -> Set[ChallengeCategory]:
        return self.__categories

    @property
    def challenges(self) -> Set[Challenge]:
        return set().union(*(c.challenges for c in self.categories))

    def get_challenge(self, challenge_slug: str) -> Optional[Challenge]:
        for challenge in self.challenges:
            if challenge.slug == challenge_slug:
                return challenge
        return None

    @property
    def flag_manager(self) -> FlagManager:
        return self.__flag_manager

    @property
    def secret_key(self) -> str:
        # todo: implement per-event secret
        return "super secret key"

    @staticmethod
    def from_directory(directory: str) -> 'Event':
        if not os.path.isdir(directory) or not os.path.isfile(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read()
        f.close()

        logo: Optional[bytes] = None
        if os.path.isfile(os.path.join(directory, 'logo')):
            f = open(os.path.join(directory, 'logo'), 'rb')
            logo = f.read()
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

        return Event(name, categories, logo)

    @property
    def logo(self) -> Optional[bytes]:
        return self.__logo
