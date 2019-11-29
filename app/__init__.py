import json
import os
import shutil
from pathlib import Path

from flask import Flask, redirect, render_template, request
from flask.helpers import make_response
from flask.json import jsonify
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

from .config import cfg
from .forms import UploadForm
from .utils import get_folders, get_sudoers, get_user, log

app = Flask(__name__)
Bootstrap(app)

META = '<meta http-equiv="refresh" content="3;url=/files">'
META2 = '<meta http-equiv="refresh" content="5;url=/files">'


@app.route("/", methods=["GET"])
def index():
    folder_choices = get_folders()

    log("User %r opened index", get_user())
    return render_template("new.html", folders=folder_choices)


@app.route("/upload", methods=["POST"])
def upload():
    form = request.form
    files = request.files.getlist("file")

    # is_ajax = False
    # if form.get("__ajax", None) == "true":
    #     is_ajax = True

    folder = request.form.get("folder")

    folder_choices = [x.as_posix() for x in get_folders()]

    if not folder:
        return {"message": "No folder supplied"}, 400

    folder = Path(folder).as_posix()
    if folder not in folder_choices:
        return {"message": "Invalid folder: %r" % folder}, 400
    if not files:
        return {"message": "No files supplied"}, 400

    for file in request.files.getlist("file"):
        save_file(file, folder)

    return ajax_response(True, "File uploaded")


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(status=status_code, msg=msg,))


def save_file(file, folder):
    filename = secure_filename(file.filename)
    filename = cfg.CLOUD_PATH / folder / filename
    file.save(filename.as_posix())

    log(
        "User %r upload files to folder %r: %s",
        get_user(),
        folder,
        secure_filename(file.filename)
        # [secure_filename(x.filename) for x in request.files.getlist("files")],
    )
    return redirect("/")


@app.route("/d/<path:filepath>", methods=["GET"])
@app.route("/delete/<path:filepath>", methods=["GET"])
def delete(filepath):
    filepath = cfg.CLOUD_PATH / filepath

    try:
        if filepath.is_dir():
            shutil.rmtree(filepath)
            log("User %r removed tree %r", get_user(), filepath.as_posix())
            return f"{META}<h1>Tree removed</h1> {filepath.as_posix()}", 200
        else:
            os.remove(filepath)
            log("User %r removed file %r", get_user(), filepath.as_posix())
            return f"{META}<h1>File deleted</h1>  {filepath.as_posix()}", 200
    except FileNotFoundError:
        log("User %r tried to incorrectly remove %r", get_user(), filepath.as_posix())
        return f"{META2}<h1>File not found</h1> {filepath.as_posix()}", 404


@app.route("/md/<path:folder>", methods=["GET"])
@app.route("/mk/<path:folder>", methods=["GET"])
@app.route("/mkdir/<path:folder>", methods=["GET"])
def mkdir(folder: str):
    os.makedirs(cfg.CLOUD_PATH / folder)

    log("User %r made dir %r", get_user(), folder)
    return redirect("/files")


@app.route("/mv", methods=["GET"])
@app.route("/move", methods=["GET"])
def move():
    _from = request.args.get("from")
    _to = request.args.get("to")

    if not _from:
        log('User %r tried to move, but forgot "from" argument', get_user())
        return '<h1>Missing "from" argument</h1>', 400

    if not _to:
        log('User %r tried to move, but forgot "to" argument', get_user())
        return '<h1>Missing "to" argument</h1>', 400

    real_from = cfg.CLOUD_PATH / _from
    real_to = cfg.CLOUD_PATH / _to

    try:
        shutil.move(real_from, real_to)
        log("User %r moved file %r to %r", get_user(), _from, _to)
        return f"{META}<h1>File moved correctly</h1>", 200
    except FileNotFoundError as err:
        log(
            "User %r tried to move file %r to %r, but failed (%r)",
            get_user(),
            _from,
            _to,
            err,
        )
        return f"{META2} File not found", 400
