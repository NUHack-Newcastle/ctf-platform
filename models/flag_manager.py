from __future__ import annotations
from models.challenge import Challenge
import hmac
import hashlib


class FlagManager:
    def __init__(self, event: Event):
        self.__event: Event = event

    def generate_flag(self, challenge: Challenge) -> str:
        assert challenge in self.__event.challenges
        signature = hmac.new(self.__event.secret_key.encode('utf-8'),
                             # todo: include team id in signature to make flag different per-team
                             msg=";".join(['ctf', self.__event.name, challenge.slug]).encode('utf-8'),
                             digestmod=hashlib.sha256
                             ).hexdigest().lower()[:16]
        return f"flag{{{signature}}}"
