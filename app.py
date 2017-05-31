import os
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

from dao import DAO

IMAGE_UPLOAD_FOLDER = 'static/images/'
AUDIO_UPLOAD_FOLDER = 'audio'
ALLOWED_EXTENSIONS_AUDIO = set(['mp3'])
ALLOWED_EXTENSIONS_PIC = set(['jpg', 'png', 'jpeg'])

app = Flask(__name__)
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER
app.config['SECRET_KEY'] = '\x0bE\x85\xed\xb0\xa5\xda\x90\xb2\x94\xd0\x02\x96\xda=\xf1\x83w\x9ei\xc3#|\xa2'

#set up a global for audio. 

@app.route('/<uid_str>', methods=['POST'])
def query_picture_position(uid_str):
    '''
       Takes the (x,y) tuple from post and retrieves the audio if near
    '''
    x = request.values['x']
    y = request.values['y']

    pos_audio = check_audio(x,y)
    print(pos_audio)
    if pos_audio is not None:
        play(pos_audio)
    return uid_str
    

def check_audio(x,y):
    audio = DAO().fetch(x,y)
    if audio is not 'None' and audio is not None:
       return audio

def play(filename):
    return "Play Hello"
 
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
            coords = DAO().fetch_xy(uid)
            return render_template('record.html', record=fname, coords=coords)

    if request.method == 'GET':
        fname = None
        for f in os.listdir(app.config['IMAGE_UPLOAD_FOLDER']):
            if f[:len(uid)] == uid:
                fname = f
        coords = DAO().fetch_xy(uid)
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
            return redirect(url_for('get_files'))
     
