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
    RealMedia parser
    Based on http://www.multimedia.cx/rmff.htm

"""

# Only implement required information to retrieve video and audio information

import struct
import cStringIO


# For testing
if __name__ == "__main__":
    import sys; sys.path.append('../../'); sys.path.append('..')


import videoparser.plugins as plugins
import videoparser.streams as streams


class Parser(plugins.BaseParser):
    _endianess = streams.endian.big
    _file_types = ['rm']
    
    def __init__(self):
        plugins.BaseParser.__init__(self)

    def parse(self, filename, video):
        stream = streams.factory.create_filestream(filename,
                                                   endianess=self._endianess)

        self.parse_objects(stream)

        
    
    def parse_objects(self, stream):

        while stream.bytes_left():
            id = stream.read_dword()
            size = stream.read_uint32()
            data = stream.read_subsegment(size - 8)
            
            if id == '.RMF':
                obj = self.parse_header(data)
            
            elif id == 'PROP':
                obj = self.parse_fileproperties(data)
            
            elif id == 'MDPR':
                obj = self.parse_mediaproperties(data)
            
            elif id == 'CONT':
                obj = self.parse_contentdescription(data)
            
            elif id == 'DATA':
                obj = None
            
            elif id == 'INDX':
                obj = None
        
            print ">> ", obj
        return True


    def parse_header(self, data):
        return None

    def parse_fileproperties(self, data):
        obj = self.FileProperties()

        obj.version = data.read_uint16()
        
        if obj.version == 0:
          obj.max_bit_rate = data.read_uint32()
          obj.avg_bit_rate = data.read_uint32()
          obj.max_packet_size = data.read_uint32()
          obj.avg_packet_size = data.read_uint32()
          obj.num_packets = data.read_uint32()
          obj.duration = data.read_uint32()
          obj.preroll = data.read_uint32()
          obj.index_offset = data.read_uint32()
          obj.data_offset = data.read_uint32()
          obj.num_streams = data.read_uint16()
          obj.flags = data.read_uint16()
    
        return obj
    
    def parse_mediaproperties(self, data):
        return None
    
    def parse_contentdescription(self, data):
        return None
    
    
    
    class FileProperties(object):
        def __repr__(self):
            buffer  = "FileProperties structure:\n"
            buffer += " %-30s: %s\n" % ('Version', self.version)
            buffer += " %-30s: %s\n" % ('Max Bitrate', self.max_bit_rate)
            buffer += " %-30s: %s\n" % ('Avg Bitrate', self.avg_bit_rate)
            buffer += " %-30s: %s\n" % ('Max packet size', self.max_packet_size)
            buffer += " %-30s: %s\n" % ('Avg packet size', self.avg_packet_size)
            buffer += " %-30s: %s\n" % ('Num packets', self.num_packets)
            buffer += " %-30s: %s\n" % ('Duration', self.duration)
            buffer += " %-30s: %s\n" % ('Preroll', self.preroll)
            buffer += " %-30s: %s\n" % ('Index offset', self.index_offset)
            buffer += " %-30s: %s\n" % ('Data offset', self.data_offset)
            buffer += " %-30s: %s\n" % ('Num streams', self.num_streams)
            buffer += " %-30s: %s\n" % ('Flags', self.flags)
            
            return buffer
        
        
if __name__ == "__main__":
    import sys
    import videofile
    
    video = videofile.VideoFile()
    p = Parser()
    p.parse(sys.argv[1], video)

    print video
    


