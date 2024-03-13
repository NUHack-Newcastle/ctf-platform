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
    def from_directory(directory: str, allow_recreate_icon_symlink=True) -> 'ChallengeCategory':
        if not os.path.isdir(directory) or not os.path.isfile(os.path.join(directory, 'name')):
            raise FileNotFoundError()

        f = open(os.path.join(directory, 'name'), 'r')
        name = f.read()
        f.close()

        icon: Optional[Icon] = None
        if os.path.isfile(os.path.join(directory, 'icon')):
            if os.path.islink(os.path.join(directory, 'icon')):
                realpath = os.path.realpath(os.path.join(directory, 'icon'))
                if os.path.basename(realpath) == 'icon_bootstrap':
                    f = open(realpath, 'r')
                    icon = IconBootstrap(f.read())
                    f.close()
                else:
                    sys.stderr.write("Warning: category icon is link to unknown name, not sure how to proceed. Omitting\n")
            elif allow_recreate_icon_symlink:
                f = open(os.path.join(directory, 'icon'), 'r')
                symlinkpath = f.read().strip()
                filepath = os.path.normpath(os.path.join(directory, symlinkpath))
                f.close()
                if os.path.isfile(filepath):
                    sys.stderr.write(f"Warning: category icon is not link, but likely symlink to '{filepath}'. Recreating\n")
                    os.remove(os.path.join(directory, 'icon'))
                    os.symlink(symlinkpath, os.path.join(directory, 'icon'))
                    return ChallengeCategory.from_directory(directory, allow_recreate_icon_symlink=False)
                else:
                    sys.stderr.write(f"Warning: category icon is not link, failed recreate to path {filepath}. Not sure how to proceed. Omitting\n")
            else:
                sys.stderr.write("Warning: category icon is not link, not sure how to proceed. Omitting\n")
        return ChallengeCategory(slug=os.path.split(directory)[-1], name=name, icon=icon)
