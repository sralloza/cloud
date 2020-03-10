from collections import namedtuple

from flask.globals import request
from flask.helpers import flash
from flask.templating import render_template
from werkzeug.utils import secure_filename

from app.config import cfg
from app.forms import UploadForm
from app.utils import get_folders, get_user, log

from . import base_blueprint

template_name = "index.html"
Folder = namedtuple("Folder", ["id", "name"])


@base_blueprint.route("/", methods=["GET"])
def index():
    form = UploadForm()
    folder_choices = get_folders()
    folder_choices = [Folder(i, x.as_posix()) for i, x in enumerate(get_folders())]
    # form.folder.choices = [(i, x.as_posix()) for i, x in enumerate(folder_choices)]

    if request.method == "GET":
        log("User %r opened index", get_user())
        return render_template(template_name, form=form, folders=folder_choices)

    if form.folder.data is None:
        flash("No folder supplied or an invalid folder was supplied", "danger")
        return render_template(template_name, form=form)

    folder_choices = get_folders()

    try:
        folder = folder_choices[int(form.folder.data)]
    except IndexError:
        flash("Invalid index folder", "danger")
        return render_template(template_name, form=form)
    files = request.files.getlist("files")

    if not files:
        flash("No files supplied", "danger")
        return render_template(template_name, form=form)

    for f in files:
        filename = secure_filename(f.filename)
        filename = cfg.CLOUD_PATH / folder / filename
        f.save(filename.as_posix())

    log(
        "User %r upload files to folder %r: %s",
        get_user(),
        folder.as_posix(),
        [secure_filename(x.filename) for x in request.files.getlist("files")],
    )
    flash("Files uploaded successfully", "success")
    return render_template(template_name, form=form)
