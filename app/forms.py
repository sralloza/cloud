from flask_wtf import FlaskForm as Form
from wtforms import FileField, SubmitField, SelectField, MultipleFileField

class UploadForm(Form):
    # file = FileField(u'File')
    files = MultipleFileField('Files')
    folder = SelectField('folder', coerce=int)
    submit = SubmitField('Upload')


