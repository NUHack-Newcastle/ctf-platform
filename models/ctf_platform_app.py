import os

from flask import Flask, render_template
from flask_login import current_user
from werkzeug.exceptions import HTTPException

from models.event import Event


class CTFPlatformApp(Flask):
    def __init__(self, event: Event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__event = event
        self.context_processor(lambda: dict(event=self.event,
                                            current_user=current_user,
                                            static_file_exists=lambda f: os.path.isfile(os.path.join("static/", f))))
        self.errorhandler(HTTPException)(lambda e: render_template('http-error.html', error=e))

    @property
    def event(self) -> Event:
        return self.__event
