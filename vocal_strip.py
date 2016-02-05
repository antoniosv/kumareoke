from subprocess import call, Popen, PIPE
import argparse
import sys
import os
from pygame import mixer

parser = argparse.ArgumentParser(description='Input song filename w/vocals')
parser.add_argument('filename', metavar='f', type=str, help='filename of the song with the vocals to be removed')
args = parser.parse_args()

print "Stripping vocal from track " + (args.filename)

# Preparing karaoke filename
fkaraoke = os.path.splitext(args.filename)[0] + ' (karaoke).mp3'

def stripw_args():
    try:
        retcode = call(["sox", args.filename, fkaraoke, "oops"])
        # if retcode < 0:
        #     print >> sys.stderr, "Child was terminated by signal", -retcode
        # else:
        #     print >> sys.stderr, "Child returned", retcode
    except OSError as e:
        print >> sys.stderr, "Execution failed:", e

def stripw_stdin():
    try:
        print 'Writing to ' + fkaraoke
        full_track = open(args.filename).read()        

        #proc = Popen(["sox", "-t .mp3", "-", "-t .mp3", "-", "oops"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        proc = Popen(["sox", "-t", ".mp3", "-", "-t", ".mp3", "-", "oops"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        #proc = Popen(["ls", "-l"], stdout=PIPE, stderr=PIPE)
        karaoke, err = proc.communicate(full_track)
        ret_code = proc.wait()

        new_file = open(fkaraoke, 'w')
        new_file.write(karaoke)
        new_file.close()

        # written_file = open(fkaraoke)
        # print written_file.read()

        # print ret_code
        
        # mixer.init()
        # mixer.music.load(karaoke)
        # mixer.music.play()

        #rc = p.returncode
    except OSError as e:
        print >> sys.stderr, "Execution failed:", e


stripw_stdin()
