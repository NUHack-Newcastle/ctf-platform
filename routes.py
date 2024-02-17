from flask import Blueprint
from flask import current_app as app
from app import CTFPlatformApp
app: CTFPlatformApp

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/challenges')
def challenges():  # put application's code here
    return app.event.name


@main_blueprint.route('/challenge/<string:challenge_slug>')
def challenge(challenge_slug: str):
    return challenge_slug
