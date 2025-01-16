import flask

from dontbeeviltube.search import search
from dontbeeviltube.server import app


@app.before_request
def set_search_query():
    flask.g.search_query = flask.request.args.get("q", "")


@app.route("/search")
def route_search():
    if not flask.g.search_query:
        flask.flash("No search query provided", "error")
        return flask.redirect("/")
    return flask.render_template(
        "search.html", search_results=search(flask.g.search_query)
    )
