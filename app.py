import os

from flask_login import LoginManager
from flask_wtf import CSRFProtect

from models.ctf_platform_app import CTFPlatformApp
from models.event import Event
from models.user import User
from routes import main_blueprint
from auth import auth_blueprint
from jinja_filters import custom_filters


def create_app() -> CTFPlatformApp:
    new_app = CTFPlatformApp(Event.from_directory('event'), __name__)
    new_app.register_blueprint(main_blueprint)
    new_app.register_blueprint(auth_blueprint)

    new_app.config['SECRET_KEY'] = 'secret'
    if 'CTF_DB_CONNECTION_STRING' not in os.environ:
        print("'CTF_DB_CONNECTION_STRING' not set, defaulting to sqlite local")
    new_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('CTF_DB_CONNECTION_STRING', 'sqlite:///db.sqlite')
    new_app.jinja_env.filters.update(custom_filters)
    new_app.jinja_env.add_extension('jinja2.ext.do')

    csrf = CSRFProtect(new_app)

    from db import db
    db.init_app(new_app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(new_app)

    @login_manager.user_loader
    def load_user(username):
        return User.query.get(username)

    with new_app.app_context():
        db.create_all()

    return new_app


app = create_app()

if __name__ == '__main__':
    app.run()
