from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import bcrypt
import flask
import flask_login
from flask_login import LoginManager, UserMixin

from dontbeeviltube.data import USERNAME_PASSWORD_WRONG
from dontbeeviltube.database import db
from dontbeeviltube.util import must


@dataclass
class User(UserMixin):
    user_id: int
    username: str
    flask_login_id: UUID

    def get_id(self) -> str:
        return str(self.flask_login_id)

    @staticmethod
    def from_flask_login_id(flask_login_id: UUID) -> User:
        with db.cursor() as curs:
            curs.execute(
                "SELECT account_id, login_name FROM accounts WHERE flask_login_id = %s",
                (str(flask_login_id),),
            )
            rec = must(curs.fetchone())
        return User(
            user_id=rec.account_id,
            username=rec.login_name,
            flask_login_id=flask_login_id,
        )

    @staticmethod
    def create_and_login(username: str, password: str) -> User:
        with db.cursor() as curs:
            curs.execute(
                "INSERT INTO accounts (login_name, password_bcrypt) VALUES (%s, %s) RETURNING flask_login_id",
                (username, bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()),
            )
            login_id = UUID(must(curs.fetchone()).flask_login_id)
        assert flask_login.login_user(
            user := User.from_flask_login_id(login_id), remember=True
        )
        return user

    @staticmethod
    def login(username: str, password: str) -> Optional[User]:
        with db.cursor() as curs:
            curs.execute(
                "SELECT account_id, password_bcrypt, flask_login_id FROM accounts WHERE login_name = %s",
                (username,),
            )
            if not (rec := curs.fetchone()):
                flask.flash(USERNAME_PASSWORD_WRONG, "error")
                return None
        if not bcrypt.checkpw(password.encode(), rec.password_bcrypt.encode()):
            flask.flash(USERNAME_PASSWORD_WRONG, "error")
            return None
        assert flask_login.login_user(
            user := User(
                user_id=rec.account_id,
                username=username,
                flask_login_id=rec.flask_login_id,
            ),
            remember=True,
        )
        return user


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    try:
        return User.from_flask_login_id(UUID(user_id))
    except Exception:
        return None
