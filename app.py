import os
import sys

import requests
from azure.storage.blob import BlobServiceClient
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from sqlalchemy.exc import PendingRollbackError

from models.config import Config
from models.ctf_platform_app import CTFPlatformApp
from models.event import Event
from models.user import User
from orchestrator import orchestrator_blueprint
from routes import main_blueprint
from auth import auth_blueprint
from jinja_filters import custom_filters
from db import db


def create_app() -> CTFPlatformApp:
    new_app = CTFPlatformApp(Event.from_directory('event'), __name__)
    if os.environ.get('CTF_IS_ORCHESTRATOR', 'false') == 'true':
        sys.stderr.write("Running as orchestrator\n")
        new_app.blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_BLOB_CONNECTION_STRING'))
        new_app.register_blueprint(orchestrator_blueprint)
    else:
        sys.stderr.write("Running as platform\n")
        new_app.register_blueprint(main_blueprint)
        new_app.register_blueprint(auth_blueprint)

    new_app.config['SECRET_KEY'] = 'secret'
    if 'CTF_DB_CONNECTION_STRING' not in os.environ:
        sys.stderr.write("'CTF_DB_CONNECTION_STRING' not set, defaulting to sqlite local\n")
    else:
        sys.stderr.write("'CTF_DB_CONNECTION_STRING' is set, attempting to use\n")
    new_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('CTF_DB_CONNECTION_STRING', 'sqlite:///db.sqlite')
    new_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 15*60
    }
    new_app.jinja_env.filters.update(custom_filters)
    new_app.jinja_env.add_extension('jinja2.ext.do')

    csrf = CSRFProtect(new_app)
    csrf.exempt(orchestrator_blueprint)

    db.init_app(new_app)

    @new_app.teardown_request
    def teardown_request(exception=None):
        db_session = db.session
        if db_session is not None:
            if exception is None:
                db_session.commit()
            else:
                db_session.rollback()
            db_session.close()

    def log_pending_transactions(session):
        # Check if there are any pending transactions
        if session.transaction is not None and session.transaction._state != 'committed':
            # Get information about the pending transaction
            pending_transaction = session.transaction
            print("Pending transaction details:")
            print("Is active:", pending_transaction.is_active)
            print("Is prepared:", pending_transaction.is_prepared)
            print("Is pending:", pending_transaction.is_pending)

            # Print changes made in the pending transaction
            print("New objects:")
            for obj in session.new:
                print(obj)
            print("Dirty objects:")
            for obj in session.dirty:
                print(obj)
            print("Deleted objects:")
            for obj in session.deleted:
                print(obj)

    @new_app.errorhandler(PendingRollbackError)
    def handle_pending_rollback_error(error):
        print("PendingRollbackError: Can't reconnect until invalid transaction is rolled back.")
        print("Pending transaction details:")
        log_pending_transactions(db.session)
        return "An error occurred. Please try again later.", 500

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(new_app)

    @login_manager.user_loader
    def load_user(username):
        return User.query.get(username)

    with new_app.app_context():
        db.create_all()
        if os.environ.get('CTF_IS_ORCHESTRATOR', 'false') != 'true':
            if Config.get_config().orchestrator_ip is None:
                sys.stderr.write("No orchestrator_ip set in config table of DB, will be unable to deploy challenges!\n")
            else:
                ok = False
                r = None
                try:
                    r = requests.get(f"http://{Config.get_config().orchestrator_ip}:{Config.get_config().orchestrator_port}/", timeout=0.2)
                    ok = r.ok
                except:
                    pass
                if not ok:
                    sys.stderr.write("Failed to contact orchestrator, may be unable to deploy challenges!\n")
                else:
                    if r.text != 'CTF Orchestrator':
                        sys.stderr.write("Unknown response from orchestrator, may be unable to deploy challenges!\n")
                    else:
                        sys.stderr.write("Connected to orchestrator OK\n")


    return new_app


app = create_app()

if __name__ == '__main__':
    app.run()
