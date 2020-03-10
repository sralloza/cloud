from flask import Blueprint

files_blueprint = Blueprint("files", __name__, template_folder="templates")

from . import routes
