import base64
import json
import mimetypes
import sys
from datetime import datetime, timedelta
from json import JSONDecodeError
from typing import List

import dicebear.models
# noinspection PyUnresolvedReferences
import pylibmagic  # don't remove, required for cross-platform python-magic support
import magic
import requests
import sqlalchemy
from dicebear import DOptions
from flask import Blueprint, send_from_directory, render_template, redirect, url_for, request, abort, Response
from flask import current_app as app
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf
from requests import ReadTimeout
from werkzeug.exceptions import BadRequest
import hmac
import hashlib

from models.ctf_platform_app import CTFPlatformApp
from db import db
from models.config import Config
from models.orchestration_static import OrchestrationStatic
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
    latest_solves: List[Solve] = Solve.query.order_by(Solve.when.desc()).limit(6)
    return render_template('dashboard.html', latest_solves=latest_solves)


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
    return Response(json.dumps({'avatar': str(current_user.avatar), 'csrf': generate_csrf()}), status=200,
                    mimetype='application/json')


@main_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_blueprint.route('/scope')
@login_required
def scope():
    if app.event.scope_html is None:
        abort(404)
    return render_template('scope.html')


@main_blueprint.route('/team')
@login_required
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
    # begin orchestrate
    config = Config.get_config()
    for challenge in app.event.challenges:
        static_orch = OrchestrationStatic.query.get((new_team.slug, challenge.slug))
        if static_orch is None:
            static_orch = OrchestrationStatic(new_team, challenge)
            db.session.add(static_orch)
            db.session.commit()
        if config.orchestrator_ip is None:
            sys.stderr.write(
                "Cannot deploy {challenge.slug} for {team.slug}: No orchestrator_ip set in config table of DB!\n")
        else:
            url = f"http://{Config.get_config().orchestrator_ip}:{Config.get_config().orchestrator_port}/orchestrate/static"
            try:
                requests.post(
                    url,
                    json={'team': new_team.slug, 'challenge': challenge.slug},
                    timeout=(None, 0.1))
            except ReadTimeout:
                pass
            sys.stderr.write(f"Requested static deploy of {challenge.slug} for {team.slug} via {url}\n")
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
        if current_user.team is None or current_user.team_pending:
            return Response("You need to be accepted onto a team before you can submit flags.", status=403,
                            mimetype='text/plain')
        if current_user.team.has_solved(c):
            return Response("Your team has already solved this flag.", status=410, mimetype='text/plain')
        if app.event.flag_manager.verify_flag(c, current_user.team, request.form['flag']):
            # get multiplier
            solve_position = len(c.solves) + 1
            new_solve = Solve(current_user.team, current_user, c, datetime.now(), Solve.calculate_multiplier(solve_position))
            db.session.add(new_solve)
            db.session.commit()
            return Response(json.dumps({}), status=200, mimetype='application/json')
        return Response("Incorrect flag", status=402, mimetype='text/plain')
    else:
        return render_template('challenge.html', challenge=c,
                               orch_static=OrchestrationStatic.query.get((current_user.team.slug if current_user.team is not None else None, c.slug)))


@main_blueprint.route('/challenges')
@login_required
def challenges():
    return render_template('challenges.html')


@main_blueprint.route('/logo')
def logo():
    if app.event.logo is None:
        abort(404)

    mime_type = magic.Magic(mime=True).from_buffer(app.event.logo)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # default MIME type if not determined

    # Create a response with the bytes data and appropriate MIME type
    response = Response(app.event.logo, content_type=mime_type)

    # Set caching headers to allow caching
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour (adjust as needed)
    response.headers['Expires'] = (datetime.now() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response


@main_blueprint.route('/splash')
def splash():
    if app.event.splash is None:
        abort(404)

    mime_type = magic.Magic(mime=True).from_buffer(app.event.splash)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # default MIME type if not determined

    # Create a response with the bytes data and appropriate MIME type
    response = Response(app.event.splash, content_type=mime_type)

    # Set caching headers to allow caching
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour (adjust as needed)
    response.headers['Expires'] = (datetime.now() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response


@main_blueprint.route('/admin', methods=['GET'])
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin.html')


@main_blueprint.route('/admin/create_token', methods=['POST'])
@login_required
def create_token():
    if not current_user.is_admin:
        abort(403)
    if 'email' not in request.form:
        abort(400)
    email = request.form['email'].lower().strip()
    signature = base64.b64encode(hmac.new(app.event.secret_key.encode('utf-8'),
                                          msg=email.encode('utf-8'),
                                          digestmod=hashlib.sha256
                                          ).digest()).decode('utf-8')
    token = base64.b64encode(json.dumps({'email': email, 'signature': signature}).encode('utf-8')).decode('utf-8')
    return Response(url_for('auth.register', token=token), status=200, mimetype='text/plain')
