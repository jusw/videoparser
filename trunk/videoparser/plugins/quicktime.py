#
#  Copyright (c) 2007 Michael van Tellingen <michaelvantellingen@gmail.com>
#  All rights reserved.
# 
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. The name of the author may not be used to endorse or promote products
#     derived from this software without specific prior written permission
# 
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
#  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
#  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""
    http://msdn2.microsoft.com/en-us/library/ms779636.aspx
    
    This is a really basic parser designed to get the required information fast

"""
# For running single
if __name__ == "__main__":
    import sys
    sys.path.append('..')

import datetime

# Project modules
import videoparser.plugins as plugins
import videoparser.streams as streams

# Define the structure of the movie atom
atom_structure = {
    'ftyp':     ('Description', "validate_file_format"),
    'moov':     ('Movie atom', {
        'mvhd':     ('Movie header atom', "parse_movie_header_atom"),
        'trak':     ('Track atom', {
            'tkhd':      ('Track header atom', "parse_track_header_atom"),
            'clip':      ('Track clipping atom', {
                'crgn':     ('Clipping region atom', None),
            }),
            'matt':      ('Track matte atom', {
                'kmat':     ('Compressed matte atomm', None),
            }),
            'edts':      ('Edit atom', {
                'elst':     ('Edit list atom', None),
            }),
            'tref':      ('DescriptionHere', {
                'tmcd':       ('DescriptionHere', None)
            }),
            'mdia':      ('Media atom', {
                'mdhd':       ('Media header atom', None),
                'hdlr':       ('Media handler reference atom', "parse_handler_reference_atom"),
                'minf':       ('Video media information atom', {
                    'smhd':    ('DescriptionHere', None),
                    'gmhd':    ('DescriptionHere', None),
                    'vmhd':        ('Video media information header atom', None),
                    'hdlr':        ('Data handler reference atom', None),
                    'dinf':        ('Data information atom', {
                        'dref':         ('Data reference atom', None)
                    }),
                    'stbl':        ('Sample table atom', {
                        'stsd':         ('Sample description atom', None),
                        'stts':         ('Time-to-sample atom', None),
                        'stsc':         ('Sample-to-chunk atom', None),
                        'stsz':         ('Sample size atom', None),
                        'stco':         ('Chunk offset atom', None),
                    }),
                }),
            }),
            'udta':    ('DescriptionHere', None),
            'meta':    ('DescriptionHere', {
                'hdlr':    ('DescriptionHere', None),
                'keys':    ('DescriptionHere', None),
                'ilst':    ('DescriptionHere', None),
            }),
        }),
        'udta':    ('User data atom', None),
        'meta':    ('Metadata atom (Guess?)', {
            'hdlr':    ('Undocumented (HDLR)', None),
            'keys':    ('Undocumented (KEYS)', None),
            'ilst':    ('Undocumented (ILST)', None),
        }),
        'cmov':     ('Color table atom', None),
        'cmov':     ('Compressed movie atom', None),
        'rmra':     ('Reference movie atom', None),
    }),
    'free':     ('Description', None),
    'wide':     ('Description', None),
    'mdat':     ('Description', None),
}
    



class Parser(plugins.BaseParser):
    _endianess = streams.endian.big
    _file_types = ['mov', 'mp4']
    
    def __init__(self):
        plugins.BaseParser.__init__(self)
        self._parse_level = 0

    def parse(self, filename, video):
        stream = streams.factory.create_filestream(filename,
                                                   endianess=self._endianess)

        # Make sure that we are dealing with a quicktime file format
        if stream.read(12) != '\x00\x00\x00 ftypqt  ':
            return False
        stream.seek(0)
        
        # Build a tree with all information extracted
        try:
            data = self.parse_atom(stream, atom_tree=atom_structure)
        except AssertionError:
            raise
            return False

        # Extract required information from the tree and place it in the
        # videofile object
        self.extract_information(data, video)
        
        return True
    
    def parse_ftyp(self, data):
        print repr(data)
        
    def parse_atom(self, data, atom_tree=None):
        self._parse_level += 1
        while data.bytes_left():
            
            atom_data = None
            atom_size = data.read_uint32()
            atom_type = data.read(4)
            atom_data = data.read_subsegment(atom_size - 8)
            #print "   " * (level + 1), "'%s':    ('DescriptionHere', {" % atom_type
            
            atom_tree_item = atom_tree.get(atom_type)
            
            if not atom_tree_item:
                print "  " * (self._parse_level +1 ), "Uknown item!!!!"
                continue
            
            self.pprint("%s:" %atom_tree_item[0])
            
            if type(atom_tree_item[1]) == dict:
                self.parse_atom(atom_data, atom_tree=atom_tree_item[1])

            elif atom_tree_item[1]:
                # Is this the python way?
                # Call the method defined in the parse tree
                self._parse_level += 1
                self.__class__.__getattribute__(self, atom_tree_item[1])(atom_data)
                self._parse_level -= 1
            
                
        self._parse_level -= 1
        
    def extract_information(self, header, video):
        
        pass
    
    def validate_file_format(self, data):
        major_brand = data.read(4)
        minor_version = data.read(4)

        if major_brand != 'qt  ':
            raise AssertionError("Invalid parser for this file " + \
                                 "(major brand = %r)" % major_brand)
        
        while data.bytes_left():
            compat_brand = data.read(4)
            if compat_brand == 'qt  ':
                return
        
        raise AssertionError("Invalid parser for this file")
    
    def pprint(self, *args, **kwargs):
        print "  " * (self._parse_level + 1),
        for arg in args:
            print arg,
        print
        
    def iprint(self, name, value, last=False):
        print "  " * (self._parse_level),
        if last:
            print " -",
        else:
            print " |",

        print "%-25s: %s" % (name, value)
        
        
    def parse_movie_header_atom(self, data):
        self.iprint("Version", data.read_uint8())
        self.iprint("Flags", repr(data.read(3)))
        self.iprint("Creation time", data.read_timestamp_mac())
        self.iprint("Modification time", data.read_timestamp_mac())
        self.iprint("Time scale", data.read_uint32())
        self.iprint("Duration", data.read_uint32())
        self.iprint("Preferred rate", data.read_uint32())
        self.iprint("Preferred volume", data.read_uint16())
        self.iprint("Reserved", repr(data.read(10)))
        self.iprint("Matrix structure ", repr(data.read(36))) 
        self.iprint("Preview time", data.read_uint32())
        self.iprint("Preview duration", data.read_uint32())
        self.iprint("Poster time", data.read_uint32())
        self.iprint("Selection time", data.read_uint32())
        self.iprint("Selection duration", data.read_uint32())
        self.iprint("Current time", data.read_uint32())
        self.iprint("Next track ID", data.read_uint32(), True)


    def parse_track_header_atom(self, data):
        self.iprint("Version", data.read_uint8())
        self.iprint("Flags", repr(data.read(3)))
        self.iprint("Creation time", data.read_timestamp_mac())
        self.iprint("Modification time", data.read_timestamp_mac())
        self.iprint("Track ID", data.read_uint32())
        self.iprint("Reserved", repr(data.read(4)))
        self.iprint("Duration", data.read_uint32())
        self.iprint("Reserved", repr(data.read(8)))
        self.iprint("Layer", data.read_uint16())
        self.iprint("Alternate group", data.read_uint16())
        self.iprint("Volume", data.read_uint16())
        self.iprint("Reserved", repr(data.read(2)))
        self.iprint("Matrix structure ", repr(data.read(36))) 
        self.iprint("Track width", data.read_qtfloat_32())
        self.iprint("Track height", data.read_qtfloat_32(), True)
        
        
    def parse_handler_reference_atom(self, data):
        self.iprint("Version", data.read_uint8())
        self.iprint("Flags", repr(data.read(3)))
        self.iprint("Component type", data.read(4))
        self.iprint("Component subtype", data.read(4))
        self.iprint("Component manufacturer", data.read_uint32())
        self.iprint("Component flags", data.read_uint32())
        self.iprint("Component flags mask", data.read_uint32())
        self.iprint("Component name", data.read(data._filesize - data.tell()),
                    True)
        
        
if __name__ == "__main__":
    import sys
    import videofile
    
    import plugins
    video = videofile.VideoFile()
    p = Parser()
    if not p.parse(sys.argv[1], video):
        print "This is not a quicktime file.."
        sys.exit(1)
        
    print video
    


