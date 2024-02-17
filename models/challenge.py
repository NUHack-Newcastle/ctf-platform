import os
import json


class Challenge:
    def __init__(self, name: str):
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    @staticmethod
    def from_directory(directory: str) -> 'Challenge':
        if not os.path.isdir(directory) or not os.path.exists(os.path.join(directory, 'challenge.json')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'challenge.json'), 'r')
        json_dict = json.loads(f.read())
        f.close()

        return Challenge(json_dict['name'])
