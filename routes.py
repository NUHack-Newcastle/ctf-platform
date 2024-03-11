import json
from json import JSONDecodeError

import dicebear.models
from dicebear import DOptions
from flask import Blueprint, send_from_directory, render_template, redirect, url_for, request, abort
from flask import current_app as app
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
from werkzeug.exceptions import BadRequest

from app import CTFPlatformApp
from db import db

app: CTFPlatformApp

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/static/<path:path>')
def static(path):
    return send_from_directory('static', path)


@main_blueprint.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main_blueprint.route('/account')
def account():
    return render_template('account.html')


@main_blueprint.route('/account/avatar', methods=['POST'])
def avatar():
    if 'style' not in request.form or 'seed' not in request.form or 'options' not in request.form:
        raise BadRequest

    j = {}
    try:
        j = json.loads(request.form['options'])
    except JSONDecodeError:
        raise BadRequest

    current_user.edit_avatar(style=request.form['style'], seed=request.form['seed'], options=j)
    db.session.commit()
    return json.dumps({'avatar': str(current_user.avatar), 'csrf': generate_csrf()})


@main_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_blueprint.route('/challenge/<string:challenge_slug>')
def challenge(challenge_slug: str):
    c = app.event.get_challenge(challenge_slug)
    if c is None:
        abort(404)
    return render_template('challenge.html', challenge=c)
