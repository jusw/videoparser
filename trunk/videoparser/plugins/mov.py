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

# Define the structure of the movie atom
atom_structure = {
    'moov':     ('Movie atom', {
        'mvhd':     ('Movie header atom'),
        'trak':     ('Track atom', {
            'tkhd':      ('Track header atom'),
            'clip':      ('Track clipping atom', {
                'crgn':     ('Clipping region atom'),
            }),
            'matt':      ('Track matte atom', {
                'kmat':     ('Compressed matte atomm'),
            }),
            'edts':      ('Edit atom', {
                'elst':     ('Edit list atom'),
            }),
            'tref':      ('DescriptionHere', {
                'tmcd':       ('DescriptionHere')
            }),
            'mdia':      ('Media atom', {
                'mdhd':       ('Media header atom'),
                'hdlr':       ('Media handler reference atom'),
                'minf':       ('Video media information atom', {
                    'smhd':    ('DescriptionHere'),
                    'gmhd':    ('DescriptionHere'),
                    'vmhd':        ('Video media information header atom'),
                    'hdlr':        ('Data handler reference atom'),
                    'dinf':        ('Data information atom', {
                        'dref':         ('Data reference atom')
                    }),
                    'stbl':        ('Sample table atom', {
                        'stsd':         ('Sample description atom'),
                        'stts':         ('Time-to-sample atom'),
                        'stsc':         ('Sample-to-chunk atom'),
                        'stsz':         ('Sample size atom'),
                        'stco':         ('Chunk offset atom'),
                    }),
                }),
            }),
            'udta':    ('DescriptionHere'),
            'meta':    ('DescriptionHere', {
                'hdlr':    ('DescriptionHere'),
                'keys':    ('DescriptionHere'),
                'ilst':    ('DescriptionHere'),
            }),
        }),
        'udta':    ('User data atom'),
        'meta':    ('Metadata atom (Guess?)', {
            'hdlr':    ('Undocumented (HDLR)'),
            'keys':    ('Undocumented (KEYS)'),
            'ilst':    ('Undocumented (ILST)'),
        }),
        'cmov':     ('Color table atom'),
        'cmov':     ('Compressed movie atom'),
        'rmra':     ('Reference movie atom'),
    })
}
    
# For running single
if __name__ == "__main__":
    import sys
    sys.path.append('..')


import plugins
import streams


class Parser(plugins.BaseParser):
    _endianess = streams.BIG_ENDIAN
    
    def __init__(self):
        plugins.BaseParser.__init__(self)
        self._parse_level = 0

    def parse(self, filename, video):
        
        stream = streams.FileStream(filename, endianess=self._endianess)


        for i in range(4):
            atom_size = stream.read_uint32()
            atom_type = stream.read(4)
            
            type_data = atom_structure.get(atom_type)

            if type(type_data) == tuple:
                atom_data = stream.read_subsegment(atom_size - 8)
                self.parse_atom(atom_data, atom_tree=type_data[1])
            else:
                stream.seek(stream.tell() + atom_size - 8)

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
            
            if type(atom_tree_item) == tuple:
                print "  " * (self._parse_level +1 ), atom_tree_item[0]
            else:
                print "  " * (self._parse_level +1 ), atom_tree_item
            
            if type(atom_tree_item) == tuple:
                self.parse_atom(atom_data, atom_tree=atom_tree_item[1])
            else:
                pass
        self._parse_level -= 1
        
    def extract_information(self, header, video):
        
        pass
        
    def parse_movie_header_data(self, data):
        pass
    
        
if __name__ == "__main__":
    import sys
    import videofile
    
    import plugins
    video = videofile.VideoFile()
    p = Parser()
    p.parse(sys.argv[1], video)

    print video
    


