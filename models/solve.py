from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from db import db
from flask import current_app as app

app: 'CTFPlatformApp'


class Solve(db.Model):
    __team_column = db.Column('team', db.String(64), db.ForeignKey('team.slug'), nullable=False)
    __user_column = db.Column('user', db.String(32), db.ForeignKey('user.username'), nullable=False)
    __challenge_column = db.Column('challenge', db.String(128), nullable=False)
    when = db.Column(db.DateTime, nullable=False)
    # store double the multiplier so, we can do .5s without losing accuracy
    __multiplier_times_two = db.Column('multiplier_times_two', db.Integer, nullable=False, default=1)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            __team_column, __challenge_column,
        ),
    )

    def __init__(self, team: 'Team', user: 'User', challenge: 'Challenge', when: datetime, multiplier: float = 1.0):
        self.__team = team
        self.__user = user
        self.__challenge_column = challenge.slug
        self.when = when
        self.__multiplier_times_two = int(multiplier * 2)

    @property
    def challenge(self) -> 'Challenge':
        for challenge in app.event.challenges:
            if challenge.slug == self.__challenge_column:
                return challenge
        raise AttributeError('Challenge not found')

    @property
    def team(self) -> 'Team':
        return self.__team

    @property
    def user(self) -> 'User':
        return self.__user

    @property
    def multiplier(self) -> float:
        return float(self.__multiplier_times_two / 2)
