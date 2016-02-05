from flask import Flask, render_template, request, redirect, make_response
from werkzeug import secure_filename
from subprocess import call, Popen, PIPE
import os
import sys

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['.mp3', '.wav', '.ogg', '.flac'])

def allowed_file(filename):
    return '.' in filename and os.path.splitext(filename)[1] in ALLOWED_EXTENSIONS

def strip_vocals(wvocals, ext):  
    proc = Popen(["sox", "-t", ext, "-", "-t", ext, "-", "oops"], stdin=PIPE, stdout=PIPE, stderr=PIPE)    
    karaoke, err = proc.communicate(wvocals)
    ret_code = proc.wait()

    return karaoke

@app.route('/')
@app.route('/<name>')
def hello_world(name=None):
    return render_template('hello.html', name=name)

@app.route('/upload', methods=['POST', 'GET'])
def upload_song(name=None):
    if request.method == 'POST':
        f = request.files['full_track']
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            extension = os.path.splitext(f.filename)[1]
            fkaraoke = (os.path.splitext(f.filename)[0] + ' (karaoke)' + extension).encode('utf-8')
            instrumental = strip_vocals(f.read(), extension)
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
    app.run(host='0.0.0.0')
