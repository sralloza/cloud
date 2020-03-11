from flask import Blueprint


def test_import_blueprint():
    from app.helpers import helpers_bp

    assert isinstance(helpers_bp, Blueprint)
