from flask import Blueprint, send_from_directory, render_template, redirect, url_for, flash
from flask import current_app as app
from flask_login import login_user, current_user
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email

from app import CTFPlatformApp
from models.user import User

app: CTFPlatformApp

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or user.password != form.password.data:
            flash('Invalid username or password')
            return render_template('login.html', form=form)
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('login.html', form=LoginForm())


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    remember = BooleanField(default=True)
    submit = SubmitField()
