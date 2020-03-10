from flask import Blueprint

base_bp = Blueprint("base", __name__, template_folder="templates")

from . import routes
