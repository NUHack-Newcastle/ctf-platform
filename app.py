from models.ctf_platform_app import CTFPlatformApp
from models.event import Event
from routes import main_blueprint


def create_app() -> CTFPlatformApp:
    new_app = CTFPlatformApp(Event.from_directory('event'), __name__)
    new_app.register_blueprint(main_blueprint)
    return new_app


if __name__ == '__main__':
    app = create_app()
    app.run()
