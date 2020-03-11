import os
import shutil
from collections import namedtuple

from flask.globals import request
from flask.helpers import flash
from werkzeug.utils import redirect, secure_filename

from app.config import cfg
from app.utils import get_folders, get_post_arg, get_user, log

from . import files_bp

Folder = namedtuple("Folder", ["id", "name"])


@files_bp.route("/upload", methods=["POST"])
def upload_files():
    folder = get_post_arg("folder")

    log("User %r made a POST request to /upload", get_user())

    if folder is None:
        flash("No folder supplied or an invalid folder was supplied", "danger")
        return redirect("/")

    folders = get_folders()

    try:
        folder = folders[int(folder)]
    except (IndexError, ValueError):
        flash("Invalid index folder (index %r)" % folder, "danger")
        return redirect("/")

    files = request.files.getlist("files[]")

    if not files:
        flash("No files supplied", "danger")
        return redirect("/")

    log_files = []
    for file in files:
        filename = secure_filename(file.filename)
        if not filename:
            continue

        log_files.append(filename)
        filename = cfg.CLOUD_PATH / folder / filename
        file.save(filename.as_posix())

    if not log_files:
        flash("No files supplied", "danger")
        return redirect("/")

    log(
        "User %r upload files to folder %r: %s",
        get_user(),
        folder.as_posix(),
        log_files,
    )
    flash("Files uploaded successfully", "success")
    return redirect("/")


@files_bp.route("/d/<path:filepath>", methods=["GET"])
@files_bp.route("/delete/<path:filepath>", methods=["GET"])
def delete(filepath):
    filepath = cfg.CLOUD_PATH / filepath

    try:
        if filepath.is_dir():
            shutil.rmtree(filepath)
            log("User %r removed tree %r", get_user(), filepath.as_posix())
            return "<h1>Tree removed</h1> {filepath.as_posix()}", 200
        else:
            os.remove(filepath)
            log("User %r removed file %r", get_user(), filepath.as_posix())
            return "<h1>File deleted</h1>  {filepath.as_posix()}", 200
    except FileNotFoundError:
        log("User %r tried to incorrectly remove %r", get_user(), filepath.as_posix())
        return "<h1>File not found</h1> {filepath.as_posix()}", 404


@files_bp.route("/md/<path:folder>", methods=["GET"])
@files_bp.route("/mk/<path:folder>", methods=["GET"])
@files_bp.route("/mkdir/<path:folder>", methods=["GET"])
def mkdir(folder: str):
    os.makedirs(cfg.CLOUD_PATH / folder)

    log("User %r made dir %r", get_user(), folder)
    return redirect("/cloud")


@files_bp.route("/mv", methods=["GET"])
@files_bp.route("/move", methods=["GET"])
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
        return "<h1>File moved correctly</h1>", 200
    except FileNotFoundError as err:
        log(
            "User %r tried to move file %r to %r, but failed (%r)",
            get_user(),
            _from,
            _to,
            err,
        )
        return " File not found", 400
