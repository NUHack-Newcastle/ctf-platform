from flask import Flask
from models.event import Event


class CTFPlatformApp(Flask):
    def __init__(self, event: Event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__event = event

    @property
    def event(self) -> Event:
        return self.__event
