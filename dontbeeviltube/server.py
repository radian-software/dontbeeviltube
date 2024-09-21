import flask

from dontbeeviltube.config import cfg
from dontbeeviltube.user import login_manager


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = cfg.flask_secret_key
login_manager.init_app(app)


import dontbeeviltube.routes.auth
import dontbeeviltube.routes.search
import dontbeeviltube.routes.static
import dontbeeviltube.routes.watch
