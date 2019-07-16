from flask import Flask, request, render_template, redirect
from werkzeug import secure_filename
from .forms import UploadForm

from flask_bootstrap import Bootstrap
import os
import shutil
from time import asctime


def log(string, *args):
    timestamp = f'[{asctime()}] - {request.remote_addr} - '
    with open('/srv/private/web.log', 'at') as f:
        f.write(timestamp + string % args + '\n')


def get_user():
    auth = request.authorization
    if not auth:
        user = None
    else:
        user = auth.username
    return user


app = Flask(__name__)
Bootstrap(app)

ROOT_PATH = '/srv/private/files/'
META = '<meta http-equiv="refresh" content="3;url=/files">'
META2 = '<meta http-equiv="refresh" content="5;url=/files">'


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()

    folders = [x[0].replace('\\', '/').replace(ROOT_PATH, '') for x in os.walk(ROOT_PATH)]
    folders = [x for x in folders if x]

    if get_user() != 'allo':
        folders = [x for x in folders if not x.startswith('.')]
    form.folder.choices = [(0, './'), ] + [(i + 1, x) for i, x in enumerate(folders)]
    folder_choices = ['./'] + folders

    if form.submit.data and form.validate_on_submit():
        folder = folder_choices[int(form.folder.data)]

        for f in request.files.getlist('files'):
            filename = secure_filename(f.filename)
            f.save(os.path.join(ROOT_PATH, folder, filename))

        log('User %r upload files to folder %r: %s',
            get_user(), folder, [secure_filename(x.filename) for x in request.files.getlist('files')])
        return redirect('/')

    log('User %r opened index', get_user())
    return render_template('minimal.html', form=form)


@app.route('/d/<path:filepath>')
@app.route('/delete/<path:filepath>')
def delete(filepath):
    filepath = os.path.join(ROOT_PATH, filepath)

    try:
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
            log('User %r removed tree %r', get_user(), filepath)
            return f'{META}<h1>Tree removed</h1>{filepath}', 200
        else:
            os.remove(filepath)
            log('User %r removed file %r', get_user(), filepath)
            return f'{META}<h1>File deleted</h1>  {filepath}', 200
    except FileNotFoundError:
        log('User %r tried to incorrectly remove %r', get_user(), filepath)
        return f'{META2}<h1>File not found</h1> {filepath}', 400


@app.route('/m/<path:folder>')
@app.route('/mkdir/<path:folder>')
def mkdir(folder: str):
    os.makedirs(os.path.join(ROOT_PATH, folder))

    log('User %r made dir %r', get_user(), folder)
    return redirect('/files')


@app.route('/mv')
@app.route('/move')
def move():
    # return '<h1>Unimplemented</h1>'

    _from = request.args.get('from')
    _to = request.args.get('to')

    if not _from:
        return f'{META2}<h1>Missing "from" argument</h1>', 400

    if not _to:
        return f'{META2}<h1>Missing "to" argument</h1>', 400

    real_from = os.path.join(ROOT_PATH, _from).replace('\\', '/')
    real_to = os.path.join(ROOT_PATH, _to).replace('\\', '/')

    try:
        shutil.move(real_from, real_to)
        log('User %r moved file %r to %r', get_user(), _from, _to)
        return f'{META}<h1>File moved correctly</h1>', 200
    except FileNotFoundError as err:
        log('User %r tried to move file %r to %r, but failed', get_user(), _from, _to)
        return f'{META2} File not found', 400
