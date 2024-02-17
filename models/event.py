import os
import json
from typing import Set
from models.challenge import Challenge


class Event:
    def __init__(self, name: str, challenges: Set[Challenge]):
        self.__name: str = name
        self.__challenges: Set[Challenge] = challenges

    @property
    def name(self) -> str:
        return self.__name

    @property
    def challenges(self) -> Set[Challenge]:
        return self.__challenges

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
                challenges.add(Challenge.from_directory(os.path.join(directory, 'challenges', challenge_slug)))

        return Event(json_dict['name'], challenges)
