from flask import Blueprint


def test_import_blueprint():
    from app.base import base_bp

    assert isinstance(base_bp, Blueprint)
