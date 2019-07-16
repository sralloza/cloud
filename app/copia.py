from flask import Flask, request, render_template, redirect
from .forms import UploadForm
from flask_bootstrap import Bootstrap
import os
import shutil


app = Flask(__name__)
Bootstrap(app)

ROOT_PATH = '/srv/private/files/'


def log(x, *args):
    with open('/srv/public/a.dfsfsfe', 'at') as f:
        f.write(x % args + '\n')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()

    folders = [x[0].replace('\\', '/').replace(ROOT_PATH, '') for x in os.walk(ROOT_PATH)]
    folders = [x for x in folders if x]
    form.folder.choices = [(0, './'), ] + [(i + 1, x) for i, x in enumerate(folders)]
    folder_choices = ['./'] + folders

    if form.submit.data and form.validate_on_submit():
        log('files: %s', request.files)
        filename = request.files[form.files.name].filename.strip()
        file_data = request.files[form.files.name].read()
        folder = folder_choices[int(form.folder.data)]

        with open(os.path.join(ROOT_PATH, folder, filename), 'wb') as fh:
            fh.write(file_data)

        return redirect('/')

    return render_template('minimal.html', form=form)


@app.route('/d/<path:filepath>')
@app.route('/delete/<path:filepath>')
def delete(filepath):
    filepath = os.path.join(ROOT_PATH, filepath)
    meta = '<meta http-equiv="refresh" content="3;url=/files">'

    try:
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
            return f'{meta}<h1>Tree removed</h1>{filepath}', 200
        else:
            os.remove(filepath)
            return f'{meta}<h1>File deleted</h1>  {filepath}', 200
    except FileNotFoundError:
        return f'{meta}<h1>File not found</h1> {filepath}', 200


@app.route('/mkdir/<path:folder>')
def mkdir(folder: str):
    os.makedirs(os.path.join(ROOT_PATH, folder))
    return redirect('/files')
