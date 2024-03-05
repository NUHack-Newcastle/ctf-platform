from flask import Flask
from models.event import Event


class CTFPlatformApp(Flask):
    def __init__(self, event: Event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__event = event
        self.context_processor(lambda: dict(event=self.event))

    @property
    def event(self) -> Event:
        return self.__event
