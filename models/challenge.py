import os
import json


class Challenge:
    def __init__(self, slug: str, name: str):
        self.__slug: str = slug
        self.__name: str = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def slug(self) -> str:
        return self.__slug

    @staticmethod
    def from_directory(directory: str) -> 'Challenge':
        if not os.path.isdir(directory) or not os.path.exists(os.path.join(directory, 'challenge.json')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'challenge.json'), 'r')
        json_dict = json.loads(f.read())
        f.close()

        return Challenge(slug=os.path.split(directory)[-1], name=json_dict['name'])
