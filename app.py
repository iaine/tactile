import os
import time
import json
from flask import Flask, request, redirect, url_for, render_template, flash, g
from werkzeug.utils import secure_filename


IMAGE_UPLOAD_FOLDER = 'static/tiles/'
ALLOWED_EXTENSIONS_AUDIO = set(['mp3', 'wav'])
ALLOWED_EXTENSIONS_PIC = set(['jpg', 'png', 'jpeg', 'gif', 'tif'])

#with open('./config.json', 'rb') as f:
#    config = json.load(f)

app = Flask(__name__)

#app.config.update(config)

app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER

#app.config['GITHUB_CLIENT_ID'] = ''
#app.config['GITHUB_CLIENT_SECRET'] = ''
app.config['SECRET_KEY'] = '\x0bE\x85\xed\xb0\xa5\xda\x90\xb2\x94\xd0\x02\x96\xda=\xf1\x83w\x9ei\xc3#|\xa2'

@app.before_first_request
def startup():
    '''
       Check for index directory file existence
    '''
    indexdir = 'static/tiles/meta/'
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
        open(indexdir + 'index.json', 'wb').close()

@app.route('/')
def query_picture_position():
    '''
       Place holder
    '''
    return redirect('/record')
    
def allowed_file(filename, extension):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extension

@app.route('/record/<uid>/json')
def get_json(uid):
    dirname = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], uid)
    filename = os.path.join(dirname, 'index.json')
    print(filename)
    data = None
    with open(filename, 'rb') as fh:
        data = json.loads(fh.read())

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/record/<uid>', methods=['GET', 'POST'])
def upload_file(uid):
    if request.method == 'POST':
        # check if the post request has the file part
        if not request.files:
            print("no file")
            flash('No file part')
            return redirect(request.url)
        file = request.files['desc']
   
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
      
            fname = None
            for f in os.listdir(dirname):
                if f[:len(uid)] == uid:
                    fname = dirname + '/'+f

            _tmp = {}
            with open(dirname + '/index.json', 'rb') as fh:
                _tmp = json.loads(fh.read())
                layout = _tmp['layout']
                coords = _tmp['points']

            _tmp['points'].append({'x':float(request.values["x"]), 'y': float(request.values["y"]), 'ONE':request.files['desc'].filename, 'TWO': request.files['detail'].filename })
            with open(dirname + '/index.json', 'wb') as fh:
                json.dump(_tmp, fh)

            return render_template('record.html', record=fname, coords=json.dumps(_tmp['points']), layout=json.dumps(_tmp['layout']) )

    if request.method == 'GET':
        fname = None
        dirname = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], uid)
        for f in os.listdir(dirname):
            if f[:len(uid)] == uid:
                fname = dirname + '/'+f
        layout = None
        coords = None
        _tmp = {}
        with open(dirname + '/index.json', 'rb') as fh:
            _tmp = json.loads(fh.read())
            layout = _tmp['layout']
            coords = _tmp['points']
        
        return render_template('record.html', record=fname, coords=json.dumps(_tmp['points']), layout=json.dumps(_tmp['layout']) )

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
            data = None
            with open('static/tiles/meta/index.json', 'r') as f:
                data = f.read()
                                   
            with open('static/tiles/meta/index.json', 'w') as f:
                if not data:
                   _tmp = {}
                   _tmp["tiles"] = []
                   _tmp["tiles"].append(fname[0])
                   json.dump(_tmp, f)
                else:
                   _tmp = json.loads(data)
                   _tmp["tiles"].append(fname[0])
                   json.dump(_tmp, f)

            #update its own index with the coordinates
            with open(os.path.join(dirname, 'index.json'), 'wb') as f:
                f.write(json.dumps({'layout': request.form['interest'], 'points': []}))

            return redirect(url_for('get_files'))
