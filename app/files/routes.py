from flask.globals import request
from werkzeug.utils import secure_filename

from app.config import cfg
from app.forms import UploadForm
from app.utils import get_folders, get_user

from . import files_blueprint


@files_blueprint.route("/upload", methods=["POST"])
def upload():
    form = UploadForm()

    if form.folder.data is None:
        return (
            "<h1>No folder supplied or an invalid folder was supplied<h1>",
            400,
        )

    folder_choices = get_folders()

    try:
        folder = folder_choices[int(form.folder.data)]
    except IndexError:
        return "<h1>Invalid index folder<h2>", 400
    files = request.files.getlist("files")

    if not files:
        return "<h1>No files supplied</h1>", 400

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
    return redirect("/")


@files_blueprint.route("/d/<path:filepath>", methods=["GET"])
@files_blueprint.route("/delete/<path:filepath>", methods=["GET"])
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
        return "<h1>File not found</h1> {filepath.as_posix()}", 404


@files_blueprint.route("/md/<path:folder>", methods=["GET"])
@files_blueprint.route("/mk/<path:folder>", methods=["GET"])
@files_blueprint.route("/mkdir/<path:folder>", methods=["GET"])
def mkdir(folder: str):
    os.makedirs(cfg.CLOUD_PATH / folder)

    log("User %r made dir %r", get_user(), folder)
    return redirect("/files")


@files_blueprint.route("/mv", methods=["GET"])
@files_blueprint.route("/move", methods=["GET"])
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
    return app

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
        return " File not found", 400
