from flask.templating import render_template

from app.forms import UploadForm
from app.utils import get_folders, get_user, log

from . import base_blueprint


@base_blueprint.route("/", methods=["GET"])
def index():
    form = UploadForm()

    folder_choices = get_folders()
    form.folder.choices = [(i, x.as_posix()) for i, x in enumerate(folder_choices)]

    log("User %r opened index", get_user())
    return render_template("minimal.html", form=form)
