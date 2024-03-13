import json
from datetime import datetime
from json import JSONDecodeError

import dicebear.models
import sqlalchemy
from dicebear import DOptions
from flask import Blueprint, send_from_directory, render_template, redirect, url_for, request, abort, Response
from flask import current_app as app
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf
from werkzeug.exceptions import BadRequest

from app import CTFPlatformApp
from db import db
from models.solve import Solve
from models.team import Team
from models.user import User

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
    return Response(json.dumps({'avatar': str(current_user.avatar), 'csrf': generate_csrf()}), status=200, mimetype='application/json')


@main_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_blueprint.route('/team')
def team():
    return render_template('team.html')


@main_blueprint.route('/team/leave', methods=['POST'])
@login_required
def leave_team():
    if current_user.team is None:
        abort(404)
    else:
        old_team = current_user.team
        current_user.team = None
        current_user.team_pending = False
        db.session.commit()
        if len(old_team.users) == 1 and old_team.users[0].team_pending:
            old_team.users[0].team_pending = False
            db.session.commit()
        if current_user.team is not None:
            abort(500)
    return Response(json.dumps({}), status=200, mimetype='application/json')


@main_blueprint.route('/team/reject', methods=['POST'])
@login_required
def team_reject():
    if 'username' not in request.form:
        abort(400)
    if current_user.team is None:
        abort(404)
    if current_user.team_pending:
        abort(403)
    user = User.query.get(request.form['username'])
    if user is None or not user.team_pending:
        abort(404)
    if current_user.team != user.team:
        abort(403)
    user.team = None
    user.team_pending = False
    db.session.commit()
    return Response(json.dumps({}), status=200, mimetype='application/json')


@main_blueprint.route('/team/join', methods=['POST'])
@login_required
def join_team():
    if 'slug' not in request.form:
        abort(400)
    if current_user.team is not None:
        abort(403)
    new_team = Team.query.get(request.form['slug'])
    if new_team is None:
        abort(404)
    current_user.team_pending = len(new_team.users) > 0
    current_user.team = new_team
    db.session.commit()
    return Response(json.dumps({}), status=200, mimetype='application/json')


@main_blueprint.route('/team/join/<string:slug>', methods=['GET'])
@login_required
def join_team_get(slug: str):
    if current_user.team is not None:
        abort(403)
    new_team = Team.query.get(slug)
    if new_team is None:
        abort(404)
    current_user.team_pending = len(new_team.users) > 0
    current_user.team = new_team
    db.session.commit()
    return redirect(url_for('main.team'))


@main_blueprint.route('/team/approve', methods=['POST'])
@login_required
def team_approve():
    if 'username' not in request.form:
        abort(400)
    if current_user.team is None:
        abort(404)
    if current_user.team_pending:
        abort(403)
    user = User.query.get(request.form['username'])
    if user is None or not user.team_pending:
        abort(404)
    if current_user.team != user.team:
        abort(403)
    user.team_pending = False
    db.session.commit()
    return Response(json.dumps({}), status=200, mimetype='application/json')


@main_blueprint.route('/team/create', methods=['POST'])
@login_required
def create_team():
    if 'name' not in request.form:
        abort(400)
    if current_user.team is not None:
        abort(403)
    new_team = Team(name=request.form['name'])
    db.session.add(new_team)
    current_user.team = new_team
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        abort(403)  # not unique
    return Response(json.dumps({}), status=200, mimetype='application/json')


@main_blueprint.route('/team/size')
@login_required
def team_size():
    if current_user.team is None:
        abort(403)
    return str(len(current_user.team.users))


@main_blueprint.route('/challenge/<string:challenge_slug>', methods=['GET', 'POST'])
@login_required
def challenge(challenge_slug: str):
    c = app.event.get_challenge(challenge_slug)
    if c is None:
        abort(404)
    if request.method == 'POST':
        if 'flag' not in request.form:
            abort(400)
        if current_user.team is None:
            abort(403)
        if current_user.team.has_solved(c):
            abort(410)
        if app.event.flag_manager.verify_flag(c, current_user.team, request.form['flag']):
            new_solve = Solve(current_user.team, current_user, c, datetime.now())
            db.session.add(new_solve)
            db.session.commit()
            return Response(json.dumps({}), status=200, mimetype='application/json')
        return Response("Incorrect flag", status=402, mimetype='text/plain')
    else:
        return render_template('challenge.html', challenge=c)

@main_blueprint.route('/challenges')
@login_required
def challenges():
    return render_template('challenges.html')
