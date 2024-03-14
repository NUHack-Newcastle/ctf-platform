import enum
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from db import db
from flask import current_app as app

from models.team import Team

app: 'CTFPlatformApp'


class OrchestrationStaticState(enum.Enum):
    NOT_STARTED = 0
    STARTED = 1
    BUILDING = 2
    UPLOADING = 3
    COMPLETE = 4
    FAILED = 5


class OrchestrationStatic(db.Model):
    __team_column = db.Column('team', db.String(64), db.ForeignKey('team.slug'), nullable=False)
    __challenge_column = db.Column('challenge', db.String(128), nullable=False)
    resources = db.Column(db.String(1024*4), nullable=True, default=None)
    state = db.Column(db.Enum(OrchestrationStaticState), nullable=False, default=OrchestrationStaticState.NOT_STARTED)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            __team_column, __challenge_column,
        ),
    )

    def __init__(self, team: 'Team', challenge: 'Challenge'):
        self.__team_column = team.slug
        self.__challenge_column = challenge.slug

    @property
    def challenge(self) -> 'Challenge':
        for challenge in app.event.challenges:
            if challenge.slug == self.__challenge_column:
                return challenge
        raise AttributeError('Challenge not found')

    @property
    def team(self) -> 'Team':
        return Team.query.get(self.__team_column)
