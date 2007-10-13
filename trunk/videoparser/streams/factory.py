import os
import stat

from videoparser.streams.binary import BinaryStream

def create_filestream(filename, endianess):
    filesize = os.stat(filename)[stat.ST_SIZE]
    
    if filesize == 0:
        raise IOError("File %s is 0 bytes!" % filename)
    fh = open(filename, 'r')
    stream = BinaryStream(fh, filesize, endianess)
    return stream


def create_stringstream(data, endianess):
    fh = cStringIO.StringIO(data)
    stream = BinaryStream(fh, len(data), endianess)
    return stream