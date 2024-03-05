from flask_login import LoginManager

from models.ctf_platform_app import CTFPlatformApp
from models.event import Event
from models.user import User
from routes import main_blueprint
from auth import auth_blueprint


def create_app() -> CTFPlatformApp:
    new_app = CTFPlatformApp(Event.from_directory('event'), __name__)
    new_app.register_blueprint(main_blueprint)
    new_app.register_blueprint(auth_blueprint)

    new_app.config['SECRET_KEY'] = 'secret'
    new_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event.db'
    from db import db
    db.init_app(new_app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(new_app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with new_app.app_context():
        db.create_all()

    return new_app


if __name__ == '__main__':
    app = create_app()
    app.run()
