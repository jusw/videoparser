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

import time
# For testing
if __name__ == "__main__":
    import sys; sys.path.append('../../'); sys.path.append('..')


import videoparser.plugins as plugins
import videoparser.streams as streams



mime_types = {
    'audio/x-pn-realaudio':     'audio',
}

class Parser(plugins.BaseParser):
    _endianess = streams.endian.big
    _file_types = ['rm']
    
    def __init__(self):
        plugins.BaseParser.__init__(self)

    def parse(self, filename, video):
        stream = streams.factory.create_filestream(filename,
                                                   endianess=self._endianess)
        
        data = self.parse_objects(stream)


        # Extract required information from the tree and place it in the
        # videofile object
        self.extract_information(data, video)
        
    
    def extract_information(self, data, video):
        
        for object in data:
            
            # Extract stream info
            if isinstance(object, self.MediaProperties):
                if object.mime_type == 'logical-fileinfo':
                    continue
                if object.mime_type != 'video/x-pn-realvideo':
                    continue
                
                

                    
        
    
    def parse_objects(self, stream):
        objects = []
        
        while stream.bytes_left():
            id = stream.read_fourcc()
            size = stream.read_uint32()
            
            # It seems some files have random junk data after the INDX object
            if id == '\x00\x00\x00\x00':
                break

            if id in ['.RMF', 'PROP', 'MDPR', 'CONT']: #, 'DATA']:
                data = stream.read_subsegment(size - 8)
            else:
                stream.seek(stream.tell() + size - 8)
                continue
            
            if id == '.RMF':
                obj = self._parse_realmedia_file(data)
            
            elif id == 'PROP':
                obj = self._parse_fileproperties(data)
            
            elif id == 'MDPR':
                obj = self._parse_mediaproperties(data)
            
            elif id == 'CONT':
                obj = self._parse_contentdescription(data)
            
            #elif id == 'DATA':
            #    for i in range(0, 2):
            #        print repr(data.read(10))
            objects.append(obj)
            
        return objects


    def _parse_realmedia_file(self, data):
        """  RealMedia file header (.RMF) """
        return None

    def _parse_fileproperties(self, data):
        """ Parse the File properties header (PROP) """
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
    
    def _parse_mediaproperties(self, data):
        """ Parse the  Media properties header (MDPR)"""
        obj = self.MediaProperties()
        obj.version = data.read_uint16()

        if obj.version == 0:
            obj.stream_number = data.read_uint16()
            obj.max_bit_rate = data.read_uint32()
            obj.avg_bit_rate = data.read_uint32()
            obj.max_packet_size = data.read_uint32()
            obj.avg_packet_size = data.read_uint32()
            obj.start_time = data.read_uint32()
            obj.preroll = data.read_uint32()
            obj.duration = data.read_uint32()
            obj.stream_name_size = data.read_uint8()
            obj.stream_name = data.read(obj.stream_name_size)
            obj.mime_type_size = data.read_uint8()
            obj.mime_type = data.read(obj.mime_type_size)
            obj.type_specific_len = data.read_uint32()
            
            type_data = data.read_subsegment(obj.type_specific_len)
            
            if obj.mime_type == 'video/x-pn-realvideo':
                obj.type_specific_data = self._parse_type_realvideo(type_data)
            else:
                obj.type_specific_data = type_data
            
        return obj


    def _parse_type_realvideo(self, s):
        
        # This is based on guessing, so it might not be 100% ok.
        # i still need to find the framerate (atleast i suppose it is included)
        
        print "version?", s.read_uint16()
        
        print "size %r" % s.read_uint16()
        print "type", s.read_fourcc()
        print "fourcc", s.read_fourcc()
        print "width", s.read_uint16()
        print "height", s.read_uint16()
        print "12 = ", s.read_uint16()
        print "0 = ", s.read_uint16()
        print "0 = ", s.read_uint16()
        print "fps = ", s.read_qtfloat_32()
        

                
    def _parse_contentdescription(self, data):
        """ Parse the  Content description header (CONT)"""
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
        
        
    class MediaProperties(object):
        def __repr__(self):
            buffer  = "MediaProperties structure:\n"
            buffer += " %-30s: %s\n" % ('Version', self.version)
            buffer += " %-30s: %s\n" % ('Stream number', self.stream_number)
            buffer += " %-30s: %s\n" % ('Max Bitrate', self.max_bit_rate)
            buffer += " %-30s: %s\n" % ('Avg Bitrate', self.avg_bit_rate)
            buffer += " %-30s: %s\n" % ('Max packet size',
                                        self.max_packet_size)
            buffer += " %-30s: %s\n" % ('Avg packet size',
                                        self.avg_packet_size)
            buffer += " %-30s: %s\n" % ('Start time', self.start_time)
            buffer += " %-30s: %s\n" % ('Preroll', self.preroll)
            buffer += " %-30s: %s\n" % ('Duration', self.duration)
            buffer += " %-30s: %s\n" % ('Stream name length',
                                        self.stream_name_size)
            buffer += " %-30s: %s\n" % ('Stream name', self.stream_name)
            buffer += " %-30s: %s\n" % ('Mime type length',
                                        self.mime_type_size)
            buffer += " %-30s: %s\n" % ('Mime type', self.mime_type)
            buffer += " %-30s: %s\n" % ('Type specific data length',
                                        self.type_specific_len)
            buffer += " %-30s: %r\n" % ('Type specific data',
                                        self.type_specific_data)
        
            return buffer
            
if __name__ == "__main__":
    import sys
    import videofile
    
    video = videofile.VideoFile()
    p = Parser()
    p.parse(sys.argv[1], video)

    print video
    


