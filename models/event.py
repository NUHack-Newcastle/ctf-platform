import os
import json
from typing import Set
from models.challenge import Challenge
from models.flag_manager import FlagManager


class Event:
    def __init__(self, name: str, challenges: Set[Challenge]):
        self.__name: str = name
        self.__challenges: Set[Challenge] = challenges
        self.__flag_manager: FlagManager = FlagManager(self)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def challenges(self) -> Set[Challenge]:
        return self.__challenges

    @property
    def flag_manager(self) -> FlagManager:
        return self.__flag_manager

    @property
    def secret_key(self) -> str:
        # todo: implement per-event secret
        return "super secret key"

    @staticmethod
    def from_directory(directory: str) -> 'Event':
        if not os.path.isdir(directory) or not os.path.exists(os.path.join(directory, 'event.json')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'event.json'), 'r')
        json_dict = json.loads(f.read())
        f.close()

        challenges: Set[Challenge] = set()
        if os.path.isdir(os.path.join(directory, 'challenges')):
            for challenge_slug in os.listdir(os.path.join(directory, 'challenges')):
                challenge = Challenge.from_directory(os.path.join(directory, 'challenges', challenge_slug))
                assert not any(challenge.slug == c.slug for c in challenges)
                challenges.add(challenge)

        return Event(json_dict['name'], challenges)
