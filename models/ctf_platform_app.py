import os

from flask import Flask, render_template, Response
from flask_login import current_user
from werkzeug.exceptions import HTTPException
from dicebear.models import styles as dicebear_styles

from models.event import Event


class CTFPlatformApp(Flask):
    def __init__(self, event: Event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__event = event
        self.context_processor(lambda: dict(event=self.event,
                                            current_user=current_user,
                                            static_file_exists=lambda f: os.path.isfile(os.path.join("static/", f)),
                                            dicebear_styles=dicebear_styles,
                               styles=[],
                                pre_content_scripts=[], print=print,
                               scripts=[]))
        self.errorhandler(HTTPException)(lambda e: Response(render_template('http-error.html', error=e), status=e.code))

    @property
    def event(self) -> Event:
        return self.__event
