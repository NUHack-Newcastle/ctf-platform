import datetime
import os
import json
import sys
from typing import Set, Optional

import dateparser
import pytz
from tzlocal import get_localzone

from models.challenge import Challenge
from models.challengecategory import ChallengeCategory
from models.config import Config
from models.flag_manager import FlagManager


class Event:
    def __init__(self, name: str, categories: Set[ChallengeCategory], scope_html_path: str, logo: Optional[bytes] = None,
                 start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None,
                 splash: Optional[bytes] = None, splash_border: Optional[str] = None):
        self.__name: str = name
        self.__categories: Set[ChallengeCategory] = categories
        self.__flag_manager: FlagManager = FlagManager(self)
        self.__logo: Optional[bytes] = logo
        self.__scope_html_path: str = scope_html_path
        self.__start_date: Optional[datetime.datetime] = start_date
        self.__end_date: Optional[datetime.datetime] = end_date
        self.__splash: Optional[bytes] = splash
        self.__splash_border: Optional[str] = splash_border

    @property
    def name(self) -> str:
        return self.__name

    @property
    def start_date(self) -> Optional[datetime.datetime]:
        return self.__start_date

    @property
    def end_date(self) -> Optional[datetime.datetime]:
        return self.__end_date

    @property
    def has_started(self) -> Optional[bool]:
        if self.start_date is None:
            return None
        now = datetime.datetime.now()
        return self.start_date <= now.replace(tzinfo=now.tzinfo or get_localzone())

    @property
    def has_ended(self) -> Optional[bool]:
        if self.end_date is None:
            return None
        now = datetime.datetime.now()
        return self.end_date <= now.replace(tzinfo=now.tzinfo or get_localzone())

    @property
    def scope_html(self) -> Optional[str]:
        if os.path.isfile(self.__scope_html_path):
            f = open(self.__scope_html_path, 'r')
            html = f.read()
            f.close()
            return html
        return None

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
        master_key = Config.get_config().secret_key
        return master_key[len(master_key) / 2:]

    @staticmethod
    def from_directory(directory: str) -> 'Event':
        if not os.path.isdir(directory) or not os.path.isfile(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read().strip()
        f.close()

        logo: Optional[bytes] = None
        if os.path.isfile(os.path.join(directory, 'logo')):
            f = open(os.path.join(directory, 'logo'), 'rb')
            logo = f.read()
            f.close()

        splash: Optional[bytes] = None
        if os.path.isfile(os.path.join(directory, 'splash')):
            f = open(os.path.join(directory, 'splash'), 'rb')
            splash = f.read()
            f.close()

        splash_border: Optional[str] = None
        if os.path.isfile(os.path.join(directory, 'splash_border')):
            f = open(os.path.join(directory, 'splash_border'), 'r')
            splash_border = f.read().strip()
            f.close()

        start_date: Optional[datetime.datetime] = None
        if os.path.isfile(os.path.join(directory, 'start_date')):
            f = open(os.path.join(directory, 'start_date'), 'r')
            start_date = dateparser.parse(f.read())
            if start_date.tzinfo is None:
                local_timezone = pytz.timezone('local')
                start_date = start_date.replace(tzinfo=local_timezone)
            f.close()

        end_date: Optional[datetime.datetime] = None
        if os.path.isfile(os.path.join(directory, 'end_date')):
            f = open(os.path.join(directory, 'end_date'), 'r')
            end_date = dateparser.parse(f.read())
            if end_date.tzinfo is None:
                local_timezone = pytz.timezone('local')
                end_date = end_date.replace(tzinfo=local_timezone)
            f.close()

        scope_html_path: str = os.path.abspath(os.path.join(directory, 'scope.html'))

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

        return Event(name, categories, scope_html_path, logo, start_date, end_date, splash, splash_border)

    @property
    def logo(self) -> Optional[bytes]:
        return self.__logo

    @property
    def splash(self) -> Optional[bytes]:
        return self.__splash

    @property
    def splash_border(self) -> Optional[str]:
        return self.__splash_border
