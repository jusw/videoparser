import hotshot, hotshot.stats
import sys
import os.path

sys.path.append('..')

import videoparser.plugins.matroska as matroska
import videoparser.plugins.quicktime as quicktime
import videoparser.plugins.avi as avi

import videoparser.videofile


try:
    filename = sys.argv[1]
except IndexError:
    print "Usage ./profiler.py <filename>"
    sys.exit(1)

ext = os.path.splitext(filename)[1][1:]

if ext in matroska.Parser._file_types:
    parser = matroska.Parser()
elif ext in avi.Parser._file_types:
    parser = avi.Parser()
elif ext in quicktime.Parser._file_types:
    parser = quicktime.Parser()
    
def parse_file(filename):

    video = videoparser.videofile.VideoFile()
    parser.parse(filename, video)


profile_file = 'plugin.prof'

prof = hotshot.Profile(profile_file)
for i in range(0, 10):
    prof.runcall(parse_file, sys.argv[1])
prof.close()


stats = hotshot.stats.load(profile_file)
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats()
