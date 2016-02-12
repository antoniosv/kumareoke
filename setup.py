# coding=utf-8
from flask import Flask, render_template, request, redirect, make_response, g, session, flash, url_for, abort, send_file
from werkzeug import secure_filename
from subprocess import call, Popen, PIPE
from contextlib import closing
import os
import sys
import sqlite3
import config

reload(sys)
sys.setdefaultencoding("utf-8")

### Initialization and configuration from file config.py
app = Flask(__name__)
app.config.update(dict(
    DATABASE = config.DATABASE,
    DEBUG = config.DEBUG,
    SECRET_KEY = config.SECRET_KEY,
    PASSPHRASE = 'lordhighlordofthefairies',
    MAX_CONTENT_LENGTH = config.MAX_CONTENT_LENGTH
))
ALLOWED_EXTENSIONS = set(['.mp3', '.wav', '.ogg', '.flac'])

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('song_schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        
def allowed_file(filename):
    return '.' in filename and os.path.splitext(filename)[1] in ALLOWED_EXTENSIONS

def strip_vocals(wvocals, ext, exp):  
    proc = Popen(["sox", "-t", ext, "-", "-t", exp, "-", "oops"], stdin=PIPE, stdout=PIPE, stderr=PIPE)    
    karaoke, err = proc.communicate(wvocals)
    ret_code = proc.wait()
    return karaoke

def add_song(title=None):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into song (title) values (?)', \
                 [title])
    g.db.commit()

@app.route('/hello')
@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('hello.html', name=name)

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('upload_song'))
    else:
        return render_template('index.html')

@app.route('/showall')
def show_songs():
    cur = g.db.execute('select title, ip from song order by id asc limit 10')
    songs = [dict(title=row[0], ip=row[1]) for row in cur.fetchall()]
    return render_template('show_songs.html', songs=songs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('logged_in'):
        return redirect(url_for('index'))    
    if request.method == 'POST':
        if request.form['passphrase'] != app.config['PASSPHRASE']:
            error = 'Contraseña equivocada'
        else:
            session['logged_in'] = True
            flash('Has ingresado exitosamente')
            return redirect(url_for('index'))        
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Su sesión ha sido terminada')
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST', 'GET'])
def upload_song(filename=None):
    if not session.get('logged_in'):
        abort(401)    
    if request.method == 'POST':
        f = request.files['full_track']
        exp = request.form.get('export')
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            if filename == '':
                filename = "Pista desconocida"
            else:
                filename = os.path.splitext(filename)[0].replace('_', ' ')
            extension = os.path.splitext(f.filename)[1]
            fkaraoke = (filename + ' (karaoke)' + exp).encode('utf-8')
            instrumental = strip_vocals(f.read(), extension, exp)
            response = make_response(instrumental)
            response.headers['Content-Type'] = "application/octet-stream"
            response.headers["Content-Disposition"] = "attachment; filename='" + fkaraoke + "'"
            #For the following to work, I need some AJAX to check the user session
            #flash('Canción ha sido convertida a karaoke exitosamente.')
            add_song(filename)
            return response
        else:
            return 'Error with file uploaded. Check extension.'
    return render_template('songupload.html', extensions=ALLOWED_EXTENSIONS)

if __name__ == '__main__':
    # host parameter grants access to other nodes in the network
    app.debug = True
    app.run(host="0.0.0.0")
