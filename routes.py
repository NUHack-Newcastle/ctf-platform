from flask import Blueprint, send_from_directory, render_template, redirect, url_for
from flask import current_app as app
from flask_login import current_user

from app import CTFPlatformApp

app: CTFPlatformApp

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/static/<path:path>')
def static(path):
    return send_from_directory('static', path)


@main_blueprint.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_blueprint.route('/challenge/<string:challenge_slug>')
def challenge(challenge_slug: str):
    return challenge_slug
