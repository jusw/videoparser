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



# Only implement required information to retrieve video and audio information

atom_container = 1
atom_leaf      = 2

#atom_types = {
#    
#    'moov':     ('Movie atom',{
#        'trak':     ('Track atom', {
#            'tkhd':     ('Track header atom'),
#        
#            'mdia':     ('Media atom', {
#                    'mdhd':     ('Media Header atom'),
#                    'hdlr':     ('Media handler reference atom')
#                    'minf':     ('Video media information atom')
#                        
#                    },
#                         
#                 
#    
#    'edts':
#    'vmhd':
#    'minf':
#    'keys':
#    'udta':
#    'ilst':
#    'tmcd':
    
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
        

    def parse(self, filename, video):
        
        stream = streams.FileStream(filename, endianess=self._endianess)


        for i in range(2):
            try:
                atom_size = stream.read_uint32()
            except:
                return
            atom_type = stream.read(4)
            atom_data = stream.read_subsegment(atom_size - 8)
            
            print atom_size, atom_type            

            
            #if atom_type == 'ftyp':
                #self.parse_ftyp(atom_data)
            
            if atom_type == 'moov':
                self.parse_atom(atom_data)
        

        return True
    
    
    def parse_ftyp(self, data):
        print repr(data)
        
    
    def parse_atom(self, data, level=0):
        while data.bytes_left():
            
            atom_data = None
            atom_size = data.read_uint32()
            atom_type = data.read(4)
            atom_data = data.read_subsegment(atom_size - 8)

            print "   " * (level + 1), atom_size, atom_type
            
            if atom_type in ['mvhd', 'tkhd', 'mdhd', 'hdlr', 'edts', 'vmhd', 
                             'dref', 'stts', 'stsd', 'stco','stsc','stsz', 'stss',
                             'keys', 'udta', 'ilst', 'tmcd', 'gmhd', 'gmin',
                             'smhd', 'dinf',
                             'taft', 'clef', 'prof', 'enof' #TrackApertureModeDimensionsAID
                             ]:
                
                pass # Process data items
            
            
            else:
                self.parse_atom(atom_data, level  +1)
            
        
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
    


