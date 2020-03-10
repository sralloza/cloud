from flask.app import Flask
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

from app.base import base_blueprint
from app.files import files_blueprint
from app.helpers import helpers_blueprint
from app.utils import gen_random_password


def create_app():
    app = Flask(__name__)
    app.secret_key = gen_random_password()
    Bootstrap(app)

    app.register_blueprint(base_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(helpers_blueprint)

    return app

app = create_app()
