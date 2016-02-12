# kumareoke
Web application to remove vocals from audio tracks. Made in Python and depends on sox and its various format handlers.

Dependencies (could work on older/newer versions):

- Python 2.7
- Flask 0.10.x
- SoX 14.4.1
- SoX format handlers for mp3, wav, ogg, and flac (install with apt-get libsox-fmt-all)

Database must be initialized beforehand with sqlite3 in the following manner:
$ sqlite3 kumareoke.db < song_schema.sql

Run web app with:
$ python setup.py

And access it on http://localhost:5000/upload
