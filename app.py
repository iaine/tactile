import os
import time
import json
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

from git import GitRepo
from dao import DAO

IMAGE_UPLOAD_FOLDER = 'static/tiles/'
#AUDIO_UPLOAD_FOLDER = 'static/tiles/audio'
ALLOWED_EXTENSIONS_AUDIO = set(['mp3'])
ALLOWED_EXTENSIONS_PIC = set(['jpg', 'png', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
#app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER
app.config['SECRET_KEY'] = '\x0bE\x85\xed\xb0\xa5\xda\x90\xb2\x94\xd0\x02\x96\xda=\xf1\x83w\x9ei\xc3#|\xa2'

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
            
            with open(os.path.join(dirname, 'index.json'), 'wb') as f:
                f.write(json.dumps({'layout': request.form['interest'], 'points': [{"x": 14, "y": 44}, {"x": 14, "y": 84}]}))
            return redirect(url_for('get_files'))
     
