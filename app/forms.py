from flask_wtf import FlaskForm as Form
from wtforms import SubmitField, SelectField, MultipleFileField


class UploadForm(Form):
    files = MultipleFileField('Files')
    folder = SelectField('folder', coerce=int)
    submit = SubmitField('Upload')
