import os
import shutil
from pathlib import Path

from flask import Flask, request, render_template, redirect
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

from .config import cfg
from .forms import UploadForm
from .utils import get_sudoers, get_user, log


app = Flask(__name__)
Bootstrap(app)

ROOT_PATH = cfg.CLOUD_PATH
META = '<meta http-equiv="refresh" content="3;url=/files">'
META2 = '<meta http-equiv="refresh" content="5;url=/files">'


def get_folders():
    folder_choices = [Path(x[0]).relative_to(ROOT_PATH) for x in os.walk(ROOT_PATH)]

    if get_user() not in get_sudoers():
        def filter_choice(x):
            return not (x.as_posix().startswith('.') and len(x.as_posix()) > 1)

        folder_choices = [x for x in folder_choices if filter_choice(x)]

    folder_choices.sort()
    return folder_choices


@app.route('/', methods=['GET'])
def index():
    form = UploadForm()

    folder_choices = get_folders()
    form.folder.choices = [(i, x.as_posix()) for i, x in enumerate(folder_choices)]

    log('User %r opened index', get_user())
    return render_template('minimal.html', form=form)


@app.route('/upload', methods=['POST'])
def upload():
    form = UploadForm()

    folder_choices = get_folders()
    folder = folder_choices[int(form.folder.data)]

    for f in request.files.getlist('files'):
        filename = secure_filename(f.filename)
        filename = ROOT_PATH / folder / filename
        f.save(filename.as_posix())

    log(
        'User %r upload files to folder %r: %s', get_user(), folder,
        [secure_filename(x.filename) for x in request.files.getlist('files')]
    )
    return redirect('/')


@app.route('/d/<path:filepath>', methods=['GET'])
@app.route('/delete/<path:filepath>', methods=['GET'])
def delete(filepath):
    filepath = ROOT_PATH / filepath

    try:
        if filepath.is_dir():
            shutil.rmtree(filepath)
            log('User %r removed tree %r', get_user(), filepath.as_posix())
            return f'{META}<h1>Tree removed</h1>{filepath.as_posix()}', 200
        else:
            os.remove(filepath)
            log('User %r removed file %r', get_user(), filepath.as_posix())
            return f'{META}<h1>File deleted</h1>  {filepath.as_posix()}', 200
    except FileNotFoundError:
        log('User %r tried to incorrectly remove %r', get_user(), filepath.as_posix())
        return f'{META2}<h1>File not found</h1> {filepath.as_posix()}', 400


@app.route('/md/<path:folder>', methods=['GET'])
@app.route('/mk/<path:folder>', methods=['GET'])
@app.route('/mkdir/<path:folder>', methods=['GET'])
def mkdir(folder: str):
    os.makedirs(ROOT_PATH / folder)

    log('User %r made dir %r', get_user(), folder)
    return redirect('/files')


@app.route('/mv', methods=['GET'])
@app.route('/move', methods=['GET'])
def move():
    _from = request.args.get('from')
    _to = request.args.get('to')

    if not _from:
        log('User %r tried to move, but forgot "from" argument', get_user())
        return '<h1>Missing "from" argument</h1>', 400

    if not _to:
        log('User %r tried to move, but forgot "to" argument', get_user())
        return '<h1>Missing "to" argument</h1>', 400

    real_from = ROOT_PATH / _from
    real_to = ROOT_PATH / _to

    try:
        shutil.move(real_from, real_to)
        log('User %r moved file %r to %r', get_user(), _from, _to)
        return f'{META}<h1>File moved correctly</h1>', 200
    except FileNotFoundError as err:
        log('User %r tried to move file %r to %r, but failed (%r)', get_user(), _from, _to, err)
        return f'{META2} File not found', 400
