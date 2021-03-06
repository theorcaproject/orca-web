import os

import flask
from flask import render_template
from flask.ext.login import login_user, logout_user, current_user

from orcaweb import app, login_manager
from orcaweb.services import api__trainer
from orcaweb.services.api__trainer import NoSession


class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


@app.route("/check")
def check():
    return "OK"


@app.before_request
def before():
    if current_user.is_authenticated():
        flask.g.server = session__get_hostname()
        flask.g.username = session__get_username()
        flask.g.region = session__get_region()



def session__get_hostname():
    return os.getenv("SERVER_URI", "http://localhost:5001")


def session__get_username():
    return flask.session.get("username")

def session__set_username(username):
    flask.session["username"] = username


def session__get_region():
    return flask.session.get("region")

def session__set_region(region):
    flask.session["region"] = region


@login_manager.user_loader
def load_user(user_id):
    return User(user_id, session__get_username())


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        authenticate_res = api__trainer.authenticate(
            session__get_hostname(), flask.request.form.get("username"), flask.request.form.get("password")
        )

        if authenticate_res:
            # Login and validate the user.
            # user should be an instance of your `User` class
            login_user(User(authenticate_res, flask.request.form.get("username")))
            session__set_username(flask.request.form.get("username"))

            settings = api__trainer.get__settings()
            if settings: session__set_region(settings["EnvName"])

            return flask.redirect("/")
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    session__set_username("")
    return flask.redirect("/")


@app.errorhandler(NoSession)
def no_session_handler(aa):
    logout_user()
    return flask.redirect("/")
