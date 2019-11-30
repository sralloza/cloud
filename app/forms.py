from flask_wtf import FlaskForm as Form
from wtforms import SubmitField, SelectField, MultipleFileField


class UploadForm(Form):
    files = MultipleFileField('files')
    folder = SelectField('folder', coerce=str)
    submit = SubmitField('upload')
