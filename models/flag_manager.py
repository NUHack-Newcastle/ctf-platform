from __future__ import annotations
import hmac
import hashlib


class FlagManager:
    def __init__(self, event: 'Event'):
        self.__event: 'Event' = event

    def generate_flag(self, challenge: 'Challenge', team: 'Team') -> str:
        assert challenge in self.__event.challenges
        signature = hmac.new(self.__event.secret_key.encode('utf-8'),
                             msg=";".join(['FLAG', self.__event.name, challenge.slug, team.slug]).encode('utf-8'),
                             digestmod=hashlib.sha256
                             ).hexdigest().lower()[:16]
        return f"flag{{{signature}}}"
