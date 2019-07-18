from flask_wtf import FlaskForm as Form
from wtforms.fields.core import UnboundField

from app import UploadForm


def test_attributes():
    assert hasattr(UploadForm, 'files')
    assert hasattr(UploadForm, 'folder')
    assert hasattr(UploadForm, 'submit')


def test_attributes_types():
    assert isinstance(UploadForm.files, UnboundField)
    assert isinstance(UploadForm.folder, UnboundField)
    assert isinstance(UploadForm.submit, UnboundField)


def test_inheritance():
    assert issubclass(UploadForm, Form)
