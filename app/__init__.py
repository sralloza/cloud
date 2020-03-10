from flask.app import Flask
from flask_bootstrap import Bootstrap

from app.base import base_blueprint
from app.files import files_blueprint
from app.helpers import helpers_blueprint
from app.utils import gen_random_password


def create_app():
    application = Flask(__name__)
    application.secret_key = gen_random_password()
    Bootstrap(application)

    application.register_blueprint(base_blueprint)
    application.register_blueprint(files_blueprint)
    application.register_blueprint(helpers_blueprint)

    return application

app = create_app()
