from flask import Blueprint


def test_import_blueprint():
    from app.files import files_bp

    assert isinstance(files_bp, Blueprint)
