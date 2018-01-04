import os
import time
import json
from flask import Flask, request, redirect, url_for, render_template, flash, g
from werkzeug.utils import secure_filename
from flask_github import GitHub

from git import GitRepo

IMAGE_UPLOAD_FOLDER = 'static/tiles/'
ALLOWED_EXTENSIONS_AUDIO = set(['mp3'])
ALLOWED_EXTENSIONS_PIC = set(['jpg', 'png', 'jpeg', 'gif'])

with open('./config.json', 'rb') as f:
    config = json.load(f)

app = Flask(__name__)

app.config.update(config)

app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER

app.config['GITHUB_CLIENT_ID'] = ''
app.config['GITHUB_CLIENT_SECRET'] = ''
app.config['SECRET_KEY'] = ''

class User():
    def __init__(self):
        self.github_access_token = ''

    def get_access(self):
        return self.github_access_token

    def set_access(self, github_access_token):
        self.github_access_token = github_access_token


github = GitHub(app)
user = User()

@app.before_first_request
def startup():
    '''
       Check for index directory file existence
    '''
    indexdir = 'static/tiles/meta/'
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
        with open(indexdir + 'index.json', 'wb') as f:
            f.write(json.dump('{"tiles": []}'))

@app.route('/')
def query_picture_position():
    '''
       Place holder
    '''
    return render_template('touch.html')
    
def allowed_file(filename, extension):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extension

@app.route('/record/<uid>', methods=['GET', 'POST'])
def upload_file(uid):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS_AUDIO):
            dirname = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], uid)
            filename = secure_filename(file.filename)
            audir = os.path.join(dirname, "audio")
            file.save(os.path.join(audir, filename))
            DAO().insert_data(uid, filename, float(request.values["x"]), float(request.values["y"]))
            fname = None
            for f in os.listdir(dirname):
                if f[:len(uid)] == uid:
                    fname = f
            layout = None
            coords = None
            with open(dirname + '/index.json', 'rb') as fh:
                _tmp = json.loads(fh.read())
                layout = _tmp['layout']
                coords = _tmp['points']
            return render_template('record.html',layout=layout, record=fname, coords=coords)

    if request.method == 'GET':
        fname = None
        dirname = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], uid)
        for f in os.listdir(dirname):
            if f[:len(uid)] == uid:
                fname = dirname + '/'+f
        layout = None
        coords = None
        with open(dirname + '/index.json', 'rb') as fh:
            _tmp = json.loads(fh.read())
            layout = _tmp['layout']
            coords = _tmp['points']

        return render_template('record.html', record=fname, coords=json.dumps(coords))

def get_records():
    data = os.listdir(app.config['IMAGE_UPLOAD_FOLDER'])
    return [datum.split('.')[0] for datum in data]

@app.route('/record', methods=['GET', 'POST'])
def get_files():
    if request.method == 'GET':
        records = get_records()
        return render_template('records.html', records=records)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS_PIC):
            filename = secure_filename(file.filename)
            fname = filename.split('.')
            dirname = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], fname[0])
            os.mkdir(dirname)
            file.save(dirname + '/' +filename)

            #update the index file
            with open(indexdir, 'wb') as f:
                _tmp = json.load(f.read())
                f.write(_tmp['tiles'].append('{"' + ' '.join(filename.split()) +'" : "' + filename + '"}'))

            #update its own index with the coordinates
            with open(os.path.join(dirname, 'index.json'), 'wb') as f:
                f.write(json.dumps({'layout': request.form['interest'], 'points': [{"x": 14, "y": 44}, {"x": 14, "y": 84}]}))

            github.post("https://api.github.com/user/repos",data={"name":fname[0]})
            #add data to local git and post to repo
            git = GitRepo(dirname)
            os.chdir(dirname)
            
            git.init()
            git.add()
            git.commit("Initial Commit")
            git.remote(fname[0], "iaine")
            git.push()
            os.chdir("../../../")

            return redirect(url_for('get_files'))

@github.access_token_getter
def token_getter():
    return user.github_access_token

@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = 'glam/record'
    if access_token is None:
        flash("Authorization failed.")
        return redirect('/')

    user.set_access(access_token)
    return redirect(next_url)

@app.route('/login')
def login():
    return github.authorize(scope="public_repo")

class User():
    def __init__(self, github_access_token):
        self.github_access_token = github_access_token
