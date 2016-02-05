from flask import Flask, render_template, request, redirect, make_response
from werkzeug import secure_filename
from subprocess import call, Popen, PIPE
import os
import sys

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['.mp3', '.wav'])

def allowed_file(filename):
    return '.' in filename and os.path.splitext(filename)[1] in ALLOWED_EXTENSIONS

def strip_vocals(wvocals):  
    proc = Popen(["sox", "-t", ".mp3", "-", "-t", ".mp3", "-", "oops"], stdin=PIPE, stdout=PIPE, stderr=PIPE)    
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
            fkaraoke = os.path.splitext(filename)[0] + ' (karaoke).mp3'
            instrumental = strip_vocals(f.read(), filename)
            response = make_response(instrumental)
            response.headers['Content-Type'] = "application/octet-stream"
            response.headers["Content-Disposition"] = "attachment; filename=" + fkaraoke
            return response
#            return render_template('songupload.html', name=instrumental.filename)
        else:
            return 'Error with file uploaded. Check extension.'
    return render_template('songupload.html')

if __name__ == '__main__':
    # host parameter grants access to other nodes in the network
    app.debug = True
    app.run(host='0.0.0.0')
