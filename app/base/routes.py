from collections import namedtuple

from flask.templating import render_template

from app.utils import get_folders, get_user, log

from . import base_bp

Folder = namedtuple("Folder", ["id", "name"])


@base_bp.route("/", methods=["GET"])
def index():
    folders = get_folders()
    folder_choices = [Folder(i, x.as_posix()) for i, x in enumerate(folders)]

    log("User %r opened index", get_user())
    return render_template("index.html", folders=folder_choices)
