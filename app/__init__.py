from flask.app import Flask
from flask_bootstrap import Bootstrap

from app.base import base_bp
from app.files import files_bp
from app.helpers import helpers_bp
from app.utils import gen_random_password


def create_app():
    application = Flask(__name__)
    application.secret_key = gen_random_password()
    Bootstrap(application)

    application.register_blueprint(base_bp)
    application.register_blueprint(files_bp)
    application.register_blueprint(helpers_bp)

    return application

app = create_app()
