import flask

from dontbeeviltube.server import app


@app.route("/")
def route_home():
    return flask.render_template("home.html")
