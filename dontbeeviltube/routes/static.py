import flask

from dontbeeviltube.server import app


@app.route("/")
def route_home():
    return flask.render_template("home.html")


@app.route("/robots.txt")
def route_robots():
    return flask.send_from_directory("static", "robots.txt")
