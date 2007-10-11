import os
import stat

from videoparser.streams.binary import BinaryStream

def create_filestream(filename, endianess):
    filesize = os.stat(filename)[stat.ST_SIZE]
    fh = open(filename, 'r')
    stream = BinaryStream(fh, filesize, endianess)
    return stream


def create_stringstream(data, endianess):
    fh = cStringIO.StringIO(data)
    stream = BinaryStream(fh, len(data), endianess)
    return stream