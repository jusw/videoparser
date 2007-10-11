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
    EBML / Matroska parser
    
    See http://www.matroska.org/technical/specs/index.html
    
    This is a really basic parser designed to get the required information fast
"""

# Future imports
from __future__ import generators

# Python built-in modules
import struct

# Project modules
import videoparser.plugins as plugins
import videoparser.streams as streams

class Types:
    string          = 1
    sub_elements    = 2
    u_integer       = 3
    float           = 4
    binary          = 5
    utf_8           = 6

types = Types()

# Only implement required information to retrieve video and audio information

#   Class-id        Element-name           Element-type
class_ids = {

    # EBML Basics
    0x1a45dfa3:     ('EBML',               types.sub_elements),
    0x4282:         ('DocType',            types.string),
    0x4287:         ('DocTypeVersion',     types.u_integer),
    0x4285:         ('DocTypeReadVersion', types.u_integer),
        
    # Global data
    0xEC:           ('Void',  types.binary),
    
    # The main elements (level 0)
    0x18538067:     ('Segment',     types.sub_elements), # Segment
    0x114D9B74:     ('SeekHead',    types.sub_elements), # Meta Seek Information
    0x1549a966:     ('Info',        types.sub_elements), # Segment Information
    0x1F43B675:     ('Cluster',     types.sub_elements), # Cluster
    0x1c53bb6b:     ('Cues',        types.sub_elements),    
        
    # Tracks (This is were we are interested in)
    0x1654AE6B:     ('Tracks',          types.sub_elements), 
    0xAE:           ('TrackEntry',      types.sub_elements),
    0xD7:           ('TrackNumber',     types.u_integer),
    0x73C5:         ('TrackUID',        types.u_integer),
    0x83:           ('TrackType',       types.u_integer),
    0xB9:           ('FlagEnabled',     types.u_integer),
    0x88:           ('FlagDefault',     types.u_integer),
    0x55AA:         ('FlagForced',      types.u_integer),
    0x9C:           ('FlagLacing',      types.u_integer),
    0x6DE7:         ('MinCache',        types.u_integer),
    0x6DF8:         ('MaxCache',        types.u_integer),
    0x23E383:       ('DefaultDuration', types.u_integer),
    0x23314F:       ('TrackTimecodeScale', types.float),
    
    0x55EE:         ('MaxBlockAdditionID',  types.u_integer),
    0x536E:         ('Name',                types.utf_8),
    0x22B59C:       ('Language',            types.string),
    0x86:           ('CodecID',             types.string),
    0x63A2:         ('CodecPrivate',        types.binary),
    0x258688:       ('CodecName',           types.utf_8),
    0x7446:         ('AttachmentLink',      types.u_integer),
    0xAA:           ('CodecDecodeAll',      types.u_integer),
    
    # Video specific elements
    0xE0:           ('Video',           types.sub_elements),
    0x1a:           ('FlagInterlaced',  types.u_integer),
    0xB0:           ('PixelWidth',      types.u_integer),
    0xBA:           ('PixelHeight',     types.u_integer),
    0x54B0:         ('DisplayWidth',    types.u_integer),
    0x54BA:         ('DisplayHeight',   types.u_integer),
    0x9A:           ('Unknown',         types.u_integer),

    # Audio specific elements
    0xE1:           ('Audio', types.sub_elements),           
    0xB5:           ('SamplingFrequency', types.float),
    0x9F:           ('Channels', types.u_integer),
}




class Parser(plugins.BaseParser):
    _endianess = streams.endian.big
    _file_types = ['mkv']
    
    def __init__(self, *args, **kwargs):
        plugins.BaseParser.__init__(self, *args, **kwargs)

        
    def parse(self, filename, video):
        in_tracks_element = False
        
        stream = streams.factory.create_filestream(filename,
                                                   endianess=self._endianess)

        # Check if this is an EBML file
        if stream.read_uint32() != 0x1a45dfa3:
            return False
        
        video.set_container('matroska')
        
        stream.seek(0)
        video_stream = None
        for elm in self.parse_header(stream):
            
            if elm is None:
                
                # Stop iterating when we have read the tracks information
                # TODO, this should be made more error-proof
                if in_tracks_element:
                    break
                
                continue
            
            key, value = elm
            if key == 'Tracks':
                in_tracks_element = True
                continue
            
            if key == 'TrackType':
                    
                if value == 1:
                    video_stream = video.new_video_stream()
                elif value == 2:
                    video_stream = video.new_audio_stream()
            
            if not video_stream:
                continue
            
            if video_stream.type == 'Video':
                if key == 'PixelWidth':
                    video_stream.set_width(value)
                if key == 'PixelHeight':
                    video_stream.set_height(value)
                
                if key == 'CodecID':
                    video_stream.set_codec(value)
            
            elif video_stream.type == 'Audio':
                if key == 'CodecID':
                    video_stream.set_codec(value)
                
                if key == 'Channels':
                    video_stream.set_channels(value)
                
                if key == 'SamplingFrequency':
                    video_stream.set_sample_rate(int(value))
        
        
        return True
            
    
    
    def parse_header(self, stream):
        
        # Elements incorporate an Element ID, a descriptor for the size of the element, and the binary data itself.
        
        while True:
            # Fetch the element id
            octet = stream.read_byte()
            if octet == '':
                raise StopIteration()
            
            classid_size, classid_bytes = self.parse_octet(octet)
            
            # Read all the bytes from the complete class-id:
            if classid_size > 1:
                class_id = stream.convert_uintvar(octet + stream.read(classid_size-1))
            else:
                class_id = ord(octet)
            
            
            # Fetch the descriptor for the size of the element
            octet = stream.read_byte()
            length_bytes, length =  self.parse_octet(octet)
            length = stream.convert_uintvar(chr(length) +
                                            stream.read(length_bytes-1))
            
            try:
                value = None
                class_name, class_type = class_ids[class_id]
                
                if class_type == types.string:
                    value = stream.read(length)
                    
                elif class_type == types.u_integer:
                    value = stream.convert_uintvar(stream.read(length))
    
                elif class_type == types.binary:
                    stream.seek(stream.tell() + length)
                
                elif class_type == types.float:
                    value = stream.read_float()
                    
                elif class_type == types.utf_8:
                    value = stream.read(length)
                    
                elif class_type == types.sub_elements:
                    if class_name in ['Info', 'SeekHead', 'Cluster', 'Cues']:
                        stream.seek(stream.tell() + length)
                        yield None
                    
                yield (class_name, value)
                
            except KeyError:
                #raise AssertionError("Unhandled class-id: %s" % hex(class_id))
                print "Unhandled class-id: %s" % hex(class_id)
                yield None
    
    
    def parse_octet(self, octet):
        """ Retrieve the length of the class-id. """
        
        octet = ord(octet)

        # The bytesize of the class-id is the number of leading 0 bits + 1
        # The value stored in this byte is with the marker bit removed (which
        #  is the highest bit)
        
        if octet == 0x00:
            return (None, None)

        # Calculate the length of the class-id            
        mask = 0x80
        length = 1
        while mask:
            if octet & mask:
                break

            length += 1
            mask >>= 1

        # return the bytesize and the value with the marker bit xor'ed out
        return (length, octet ^ 2**(8-length))
    
if __name__ == "__main__":
    import sys
    import videofile
    

    video = videofile.VideoFile()

    p = Parser(file)

    p.parse(sys.argv[1], video)

    print video

    
    

