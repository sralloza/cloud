from app.utils import add_to_hides, get_hides, remove_from_hides

from . import helpers_blueprint


@helpers_blueprint.route("/hide/<path:filepath>", methods=["GET"])
def hide(filepath):
    add_to_hides(filepath)
    return "done", 200


@helpers_blueprint.route("/show-hides", methods=["GET"])
def show_hides():
    return "<br>".join(get_hides()), 200


@helpers_blueprint.route("/unhide/<path:filepath>", methods=["GET"])
def unhide(filepath):
    remove_from_hides(filepath)
    return "done", 200


@helpers_blueprint.route("/unhide-all", methods=["GET"])
def unhide_all():
    for folder in get_hides():
        remove_from_hides(folder)
    return "done", 200
