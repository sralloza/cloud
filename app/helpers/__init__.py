from flask import Blueprint

helpers_blueprint = Blueprint("helpers", __name__, template_folder="templates")

from . import routes
