import os
import json
import sys
from typing import Set, Optional

from models.challenge import Challenge
from models.icon import Icon
from models.icon_bootstrap import IconBootstrap


class ChallengeCategory:
    def __init__(self, slug: str, name: str, icon: Optional[Icon] = None):
        self.__slug: str = slug
        self.__name: str = name
        self.__challenges: Set[Challenge] = set()
        self.__icon: Optional[Icon] = icon

    @property
    def name(self) -> str:
        return self.__name

    @property
    def slug(self) -> str:
        return self.__slug

    @property
    def challenges(self) -> Set[Challenge]:
        return self.__challenges.copy()

    @property
    def icon(self) -> Optional[Icon]:
        return self.__icon

    def add_challenge(self, challenge: Challenge):
        self.__challenges.add(challenge)

    @staticmethod
    def from_directory(directory: str) -> 'ChallengeCategory':
        if not os.path.isdir(directory) or not os.path.exists(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read()
        f.close()

        icon: Optional[Icon] = None
        if os.path.exists(os.path.join(directory, 'icon')):
            if os.path.islink(os.path.join(directory, 'icon')):
                realpath = os.path.realpath(os.path.join(directory, 'icon'))
                if os.path.basename(realpath) == 'icon_bootstrap':
                    f = open(realpath, 'r')
                    icon = IconBootstrap(f.read())
                    f.close()
                else:
                    sys.stderr.write("Warning: category icon is link to unknown name, not sure how to proceed. Omitting\n")
            else:
                sys.stderr.write("Warning: category icon is not link, not sure how to proceed. Omitting\n")
        return ChallengeCategory(slug=os.path.split(directory)[-1], name=name, icon=icon)
