from app.utils import add_to_ignored, get_ignored, remove_from_ignored

from . import helpers_bp


@helpers_bp.route("/ignore/<path:filepath>", methods=["GET"])
def ignore(filepath):
    add_to_ignored(filepath)
    return "done", 200


@helpers_bp.route("/show-ignored", methods=["GET"])
def show_ignored():
    return "<br>".join(get_ignored()), 200


@helpers_bp.route("/unignore/<path:filepath>", methods=["GET"])
def unignore(filepath):
    remove_from_ignored(filepath)
    return "done", 200


@helpers_bp.route("/un_ignore-all", methods=["GET"])
def unignore_all():
    for folder in get_ignored():
        remove_from_ignored(folder)
    return "done", 200
