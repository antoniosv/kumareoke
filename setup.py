from flask import Flask, render_template, request, redirect, make_response
from werkzeug import secure_filename
from subprocess import call, Popen, PIPE
from contextlib import closing
import os
import sys
import sqlite3
import config

### Initialization and configuration from file config.py
app = Flask(__name__)
app.config['DATABASE'] = config.DATABASE
app.config['DEBUG'] = config.DEBUG
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['PASSPHRASE'] = config.PASSPHRASE
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

ALLOWED_EXTENSIONS = set(['.mp3', '.wav', '.ogg', '.flac'])

# def connect_db():
#     return sqlite3.connect(app.config['DATABASE'])

# def init_db():
#     with closing(connect_db()) as db:
#         with app.open_resource('song_schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()

# @app.before_request
# def before_request():
#     g.db = connect_db()

# @app.teardown_request
# def teardown_request(exception):
#     db = getattr(g, 'db', None)
#     if db is not None:
#         db.close()
        
def allowed_file(filename):
    return '.' in filename and os.path.splitext(filename)[1] in ALLOWED_EXTENSIONS

def strip_vocals(wvocals, ext, exp):  
    proc = Popen(["sox", "-t", ext, "-", "-t", exp, "-", "oops"], stdin=PIPE, stdout=PIPE, stderr=PIPE)    
    karaoke, err = proc.communicate(wvocals)
    ret_code = proc.wait()
    return karaoke

@app.route('/')
@app.route('/<name>')
def hello_world(name=None):
    return render_template('hello.html', name=name)

@app.route('/showall')
def show_all():
    cur = g.db.execute('select title, ip from users order by id desc')
    songs = [dict(title=row[0], ip=row[1]) for row in cur.fetchall()]
    return render_template('show_songs.html', songs=songs)

@app.route('/upload', methods=['POST', 'GET'])
def upload_song(name=None):
    if request.method == 'POST':
        f = request.files['full_track']
        exp = request.form.get('export')
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            extension = os.path.splitext(f.filename)[1]
            fkaraoke = (os.path.splitext(f.filename)[0] + ' (karaoke)' + exp).encode('utf-8')
            instrumental = strip_vocals(f.read(), extension, exp)
            response = make_response(instrumental)
            response.headers['Content-Type'] = "application/octet-stream"
            response.headers["Content-Disposition"] = "attachment; filename='" + fkaraoke + "'"
            return response
#            return render_template('songupload.html', name=instrumental.filename)
        else:
            return 'Error with file uploaded. Check extension.'
    return render_template('songupload.html', extensions=ALLOWED_EXTENSIONS)

if __name__ == '__main__':
    # host parameter grants access to other nodes in the network
    app.debug = True
    app.run(host="0.0.0.0")
