from subprocess import call
import argparse
import sys

parser = argparse.ArgumentParser(description='Input song filename w/vocals')
parser.add_argument('filename', metavar='f', type=str, help='filename of the song with the vocals to be removed')
args = parser.parse_args()

print "Stripping vocal from track " + (args.filename)

try:
    #retcode = call("sox " + args.filename + " karaoke.mp3" + " oops")
    retcode = call(["sox", args.filename,"karaoke.mp3", "oops"])
    if retcode < 0:
        print >> sys.stderr, "Child was terminated by signal", -retcode
    else:
        print >> sys.stderr, "Child returned", retcode
except OSError as e:
    print >> sys.stderr, "Execution failed:", e

