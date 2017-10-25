import os
import time
import json
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

from dao import DAO
from audioplay import Audio

IMAGE_UPLOAD_FOLDER = 'static/images/'
AUDIO_UPLOAD_FOLDER = 'audio'
ALLOWED_EXTENSIONS_AUDIO = set(['mp3'])
ALLOWED_EXTENSIONS_PIC = set(['jpg', 'png', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER
app.config['SECRET_KEY'] = '\x0bE\x85\xed\xb0\xa5\xda\x90\xb2\x94\xd0\x02\x96\xda=\xf1\x83w\x9ei\xc3#|\xa2'

#set up a global for audio. 
state = 1
curr_time = 0

@app.route('/<uid_str>', methods=['GET', 'POST'])
def query_picture_position(uid_str):
    '''
       Takes the (x,y) tuple from post and retrieves the audio if near
    '''
    global state
    if request.method == 'GET':
        return render_template('touch.html')
    if request.method == 'POST':
        content = request.get_json(force=True)
        if state == 0:
            if 'x' in content:
                if content["x"] < 144:
                   if content["y"] < 164:
                    play('overview.mp3')
                   elif content["y"] < 194:
                    stop()
                else:        
                    pos_audio = check_audio(content["x"],content["y"])
                    print(pos_audio)
                    if pos_audio is not None:
                        play(pos_audio)
        else:
            state = 0
            stop()
        return uid_str
    

def check_audio(x,y):
    audio = DAO().fetch(x,y)
    if audio is not 'None' and audio is not None:
       return audio

def play(filename):
    if filename == "overview.mp3":
        curr_time = time.time()
        state == 3
        Audio().play(filename)
    else:
        if time.time() > (curr_time + (2 * 60 * 1000)):
            Audio().play(filename)
 
def stop():
    Audio().stop()

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
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], filename))
            DAO().insert_data(uid, filename, float(request.values["x"]), float(request.values["y"]))
            fname = None
            for f in os.listdir(app.config['IMAGE_UPLOAD_FOLDER']):
                if f[:len(uid)] == uid:
                    fname = f
            layout = None
            with open(uid + '.json', 'rb') as fh:
                _tmp = json.loads(f.read())
                layout = _tmp['layout']
            coords = [{'x':14,'y':44 }, {'x':14,'y':84 }]
            coords = DAO().fetch_xy(uid)
            return render_template('record.html',layout=layout, record=fname, coords=coords)

    if request.method == 'GET':
        fname = None
        for f in os.listdir(app.config['IMAGE_UPLOAD_FOLDER']):
            if f[:len(uid)] == uid:
                fname = f
        coords = [{'x':44,'y':44 }, {'x':44,'y':84 }]
        #coords = DAO().fetch_xy(uid)
        #coords.append({'x':0.00,'y':0.10 })
        print(coords)
        return render_template('record.html', record=fname, coords=coords)

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
            file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
            fname = filename.split('.')
            with open(fname[0] + '.json', 'wb') as f:
                f.write(json.dumps({'layout': request.form['interest']}))
            return redirect(url_for('get_files'))
     
