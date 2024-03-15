import base64
import json

from flask import Blueprint, send_from_directory, render_template, redirect, url_for, flash, abort
from flask import current_app as app
from flask_login import login_user, current_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email
import hmac
import hashlib

from models.ctf_platform_app import CTFPlatformApp
from db import db
from models.user import User

app: CTFPlatformApp

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or user.password != form.password.data:
            flash('Invalid username or password')
            return render_template('login.html', form=form)
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('login.html', form=LoginForm())


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember = BooleanField(default=True)
    submit = SubmitField()


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth_blueprint.route('/register/<string:token>', methods=['GET', 'POST'])
def register(token: str):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # check register token
    t = json.loads(base64.b64decode(token.encode('utf-8')).decode('utf-8'))
    if not ('email' in t and 'signature' in t):
        abort(400)
    real_signature = hmac.new(app.event.secret_key.encode('utf-8'),
                              msg=t['email'].encode('utf-8'),
                              digestmod=hashlib.sha256
                              ).digest()
    signature = base64.b64decode(t['signature'].encode('utf-8'))
    if signature != real_signature:
        abort(403)
    if len(User.query.filter_by(email=t['email']).all()) > 0:
        abort(410)

    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user or form.username.data.strip().lower() in ['admin']:
            flash('That username is already taken or is not allowed. Please choose another.')
        else:
            user = User(form.username.data, t['email'], form.password.data, '', 'thumbs', form.username.data, {}, None)
            db.session.add(user)
            db.session.commit()
            return render_template('register.html', register_ok=True)

    return render_template('register.html', form=RegisterForm(), email=t['email'], token=token, register_ok=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()
