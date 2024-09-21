import flask

from dontbeeviltube.server import app


@app.before_request
def set_video_id():
    flask.g.video_id = flask.request.args.get("v", "")


@app.route("/watch")
def route_watch():
    if not flask.g.video_id:
        flask.flash("No video ID provided", "error")
        return flask.redirect("/")
    return flask.render_template("watch.html", video_status="not_available")
