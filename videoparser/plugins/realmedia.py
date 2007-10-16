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
    Based on:
        - http://www.multimedia.cx/rmff.htm
        - http://wiki.multimedia.cx/index.php?title=RealMedia
"""

import struct


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
        if stream.read_fourcc() != '.RMF':
            return False
        stream.seek(0)
        
        data = self.parse_objects(stream)

        # Extract required information from the tree and place it in the
        # videofile object
        self.extract_information(data, video)
        
        return True

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


    def extract_information(self, data, video):
        for object in data:
            if isinstance(object, self.MediaProperties):
                if object.mime_type == 'logical-fileinfo':
                    continue
                
                if object.mime_type == 'audio/x-pn-realaudio':
                    stream = video.new_audio_stream()
                    data = object.type_specific_data
                    stream.set_duration(microseconds=object.duration * 1000)
                    stream.set_sample_rate(data.sample_rate)
                    stream.set_bit_per_sample(data.sample_size)
                    stream.set_channels(data.num_channels)
                    stream.set_codec(data.fourcc_string)
                    
                if object.mime_type == 'video/x-pn-realvideo':
                    stream = video.new_video_stream()
                    data = object.type_specific_data
                    stream.set_duration(microseconds=object.duration * 1000)
                    stream.set_width(data.width)
                    stream.set_height(data.height)
                    stream.set_framerate(data.fps)
                    stream.set_codec(data.codec)
                    
                    
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
            elif obj.mime_type == 'audio/x-pn-realaudio':
                obj.type_specific_data = self._parse_type_realaudio(type_data)
            else:
                obj.type_specific_data = type_data
            
        return obj


    def _parse_type_realvideo(self, data):
        
        # This is based on guessing, so it might not be 100% ok.
        # i still need to find the framerate (atleast i suppose it is included)
        
        obj = self.RealVideoProperties()
        obj.version = data.read_uint16()
        obj.size = data.read_uint16()
        obj.type = data.read_fourcc()
        obj.codec = data.read_fourcc()
        obj.width = data.read_uint16()
        obj.height = data.read_uint16()
        
        data.seek(data.tell() + 6)
        
        # Double check if this is correct for RV10/RV20 since all test files
        # return 15.0
        obj.fps = data.read_qtfloat_32()
        
        # I have no clue what the other bytes mean
        
        return obj
        
    def _parse_type_realaudio(self, data):

        # Based on information at:
        # http://wiki.multimedia.cx/index.php?title=RealMedia
        
        obj = self.RealAudioProperties()
        obj.type = data.read_dword()
        obj.version = data.read_uint16()
        
        if obj.version == 3:
            pass
        
        elif obj.version in [4, 5]:
            obj.unused = data.read_uint16()
            obj.signature =  data.read(4)
            obj.unknown_1 = data.read_uint32()
            obj.version_2 = data.read_uint16()
            obj.header_size = data.read_uint32()
            obj.codec_flavor = data.read_uint16()
            obj.codec_frame_size = data.read_uint32()
            obj.unknown_2 = data.read(12)
            obj.sub_packet = data.read_uint16()
            obj.frame_size = data.read_uint16()
            obj.sub_packet_size = data.read_uint16()
            obj.unknown_3 = data.read_uint16()
        
            if obj.version == 5:
                obj.unknown_4 = data.read(6)
            
            obj.sample_rate = data.read_uint16()
            obj.unknown_5 = data.read_uint16()
            obj.sample_size = data.read_uint16()
            obj.num_channels = data.read_uint16()
            
            if obj.version == 4:
                obj.interleaver_id_length = data.read_uint8()
                obj.interleaver_id = data.read(obj.interleaver_id_length)
                obj.fourcc_string_length = data.read_uint8()
                obj.fourcc_string = data.read(obj.fourcc_string_length)
                
            elif obj.version == 5:
                obj.interleaver_id = data.read_dword()
                obj.fourcc_string = data.read_dword()

            obj.unknown_6 = data.read(3)
            
            if obj.version == 5:
                obj.unknown_7 = data.read(1)
            
            obj.codec_extradata_length = data.read_uint32()
            obj.codec_extradata = data.read(obj.codec_extradata_length)

        return obj

                
    def _parse_contentdescription(self, data):
        """ Parse the  Content description header (CONT)"""
        return None



    class Structure(object):
        def repr_childs(self, obj):
            buffer = ""
            for entry in obj:
                buffer += "\n".join(["   %s" % line for line
                                     in repr(entry).split('\n')])
                buffer += "\n"
            return buffer

    
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
        
        
    class MediaProperties(Structure):
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
            buffer += " %-30s:\n %s" % ('Type specific data',
                                        self.repr_childs([self.type_specific_data]))
        
            return buffer
    
    
    class RealVideoProperties(Structure):
        def __repr__(self):
            buffer  = "RealVideoProperties structure:\n"
            buffer += " %-30s: %s\n" % ('Version (?)',self.version)
            buffer += " %-30s: %s\n" % ('Size',self.size)
            buffer += " %-30s: %s\n" % ('Type',self.type)
            buffer += " %-30s: %s\n" % ('Codec',self.codec)
            buffer += " %-30s: %s\n" % ('Width',self.width)
            buffer += " %-30s: %s\n" % ('Height',self.height)
            buffer += " %-30s: %s\n" % ('Frames per second',self.fps)
    
            return buffer
        
    class RealAudioProperties(Structure):
        def __repr__(self):
            buffer  = "RealAudioProperties structure:\n"
            buffer += " %-30s: %s\n" % ('Type', self.type)
            buffer += " %-30s: %s\n" % ('Version', self.version)
            
            if self.version == 3:
                pass
            
            elif self.version in [4, 5]:
                buffer += " %-30s: %s\n" % ('Unused', self.unused)
                buffer += " %-30s: %s\n" % ('Signature', self.signature)
                buffer += " %-30s: %r\n" % ('Unknown', self.unknown_1)
                buffer += " %-30s: %s\n" % ('Version 2', self.version_2)
                buffer += " %-30s: %s\n" % ('Header size', self.header_size)
                buffer += " %-30s: %s\n" % ('Codec flavor', self.codec_flavor)
                buffer += " %-30s: %s\n" % ('Codec frame size',
                                            self.codec_frame_size)
                buffer += " %-30s: %r\n" % ('Unknown', self.unknown_2)
                buffer += " %-30s: %s\n" % ('Sub-packet', self.sub_packet)
                buffer += " %-30s: %s\n" % ('Frame size', self.frame_size)
                buffer += " %-30s: %s\n" % ('Sub-packet size',
                                            self.sub_packet_size)
                buffer += " %-30s: %r\n" % ('Unknown', self.unknown_3)
            
                if self.version == 5:
                    buffer += " %-30s: %r\n" % ('Unknown', self.unknown_4)
                
                buffer += " %-30s: %s\n" % ('Sample rate', self.sample_rate)
                buffer += " %-30s: %r\n" % ('Unknown', self.unknown_5)
                buffer += " %-30s: %s\n" % ('Sample size', self.sample_size)
                buffer += " %-30s: %s\n" % ('Channels', self.num_channels)
                
                if self.version == 4:
                    buffer += " %-30s: %s\n" % ('Interleaver id length',
                                                self.interleaver_id_length)
                    buffer += " %-30s: %s\n" % ('Interleaver id',
                                                self.interleaver_id)
                    buffer += " %-30s: %s\n" % ('FourCC string length',
                                                self.fourcc_string_length)
                    buffer += " %-30s: %s\n" % ('FourCC string',
                                                self.fourcc_string)
                    
                elif self.version == 5:
                    buffer += " %-30s: %s\n" % ('Interleaver id', self.interleaver_id)
                    buffer += " %-30s: %s\n" % ('FourCC string', self.fourcc_string)
    
                buffer += " %-30s: %r\n" % ('Unknown', self.unknown_6)
                
                if self.version == 5:
                    buffer += " %-30s: %r\n" % ('Unknown', self.unknown_7)
                
                buffer += " %-30s: %s\n" % ('Codec extra data length',
                                            self.codec_extradata_length)
                buffer += " %-30s: %r\n" % ('Codec extra data',
                                            self.codec_extradata)
    
            return buffer


