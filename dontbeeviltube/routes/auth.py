import hashlib

import flask
import flask_login
from flask_wtf import FlaskForm
import requests
from wtforms import PasswordField, StringField, ValidationError
from wtforms.validators import EqualTo, InputRequired, Length

from dontbeeviltube.database import db
from dontbeeviltube.log import log_error
from dontbeeviltube.server import app
from dontbeeviltube.user import User
from dontbeeviltube.util import strip_safe


@app.before_request
def load_user():
    flask.g.user = flask_login.current_user


class NotPwned:
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        h = hashlib.sha1(field.data.encode()).hexdigest()
        try:
            resp = requests.get(
                f"https://api.pwnedpasswords.com/range/{h[:5]}", timeout=5
            )
            resp.raise_for_status()
        except Exception as e:
            log_error("HIBP check", e)
            return  # don't block account creation on this
        for line in resp.text.splitlines():
            if line[:35].lower() == h[5:]:
                num_breaches = int(line[36:])
                message = field.ngettext(
                    "Password has appeared in a public data breach already.",
                    "Password has appeared in %(num_breaches)d public data breaches already.",
                    num_breaches,
                )
                raise ValidationError(
                    message % dict(num_breaches=num_breaches),
                )


class RegisterForm(FlaskForm):

    username = StringField(
        "Username",
        filters=[strip_safe],
        validators=[
            InputRequired("Username can't be empty"),
            Length(
                min=1,
                max=64,
                message="Username must be between %(min)d and %(max)d characters",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        filters=[strip_safe],
        validators=[
            InputRequired("Password can't be empty"),
            Length(
                min=1,
                max=64,
                message="Password must be between %(min)d and %(max)d characters",
            ),
            EqualTo("confirm_password", "Passwords don't match"),
            NotPwned(),
        ],
    )

    confirm_password = PasswordField(
        "Confirm password",
        filters=[strip_safe],
        validators=[
            InputRequired(),
        ],
    )


@app.route("/auth/register", methods=["GET", "POST"])
def route_register():
    form = RegisterForm()
    if form.validate_on_submit():
        User.create_and_login(form.username.data, form.password.data)
        flask.flash("Created an account and logged you in")
        return flask.redirect("/")
    return flask.render_template("register.html", form=form)


class LoginForm(FlaskForm):

    username = StringField(
        "Username",
        filters=[strip_safe],
        validators=[
            InputRequired("Username can't be empty"),
            Length(
                min=1,
                max=64,
                message="Username must be between %(min)d and %(max)d characters",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        filters=[strip_safe],
        validators=[
            InputRequired("Password can't be empty"),
            Length(
                min=1,
                max=64,
                message="Password must be between %(min)d and %(max)d characters",
            ),
        ],
    )


@app.route("/auth/login", methods=["GET", "POST"])
def route_login():
    form = LoginForm()
    if form.validate_on_submit():
        if User.login(form.username.data, form.password.data):
            flask.flash("Logged you in")
            return flask.redirect("/")
    return flask.render_template("login.html", form=form)
