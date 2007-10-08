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


# Only implement required information to retrieve video and audio information

import struct
import StringIO
import cStringIO


LITTLE_ENDIAN = 0
BIG_ENDIAN    = 1


    
    
class BinaryReader(object):
    __slots__ = ['_endianess']
    
    def __init__(self, endianess=LITTLE_ENDIAN):
        self._endianess = endianess
        
        
    def read(self):
        raise NotImplementedError()
    
    def set_endianess(self, endianess):
        self._endianess = endianess
    
    def unpack(self, type, length):
        if self._endianess == BIG_ENDIAN:
            return struct.unpack('>' + type, self.read(length))[0]
        else:
            return struct.unpack('<' + type, self.read(length))[0]

    def read_float(self):
        return self.unpack('f', 4)

    def read_uint64(self):
        return self.unpack('Q', 8)

    def read_int64(self):
        return self.unpack('q', 4)
        
    def read_uint32(self):
        return self.unpack('I', 4)

    def read_int32(self):
        return self.unpack('i', 4)

    def read_uint16(self):
        return self.unpack('H', 2)

    def read_int16(self):
        return self.unpack('h', 2)
    
    def read_uint8(self):
        return ord(self.read(1))
    
    def read_int8(self):
        return struct.unpack('b', self.read(1))[0]
    
    def read_dword(self):
        return self.read(4)
    
    def read_word(self):
        return self.read(2)
    
    def read_qword(self):
        return self.read(8)
    
    def read_byte(self):
        return self.read(1)
        
    # TODO: FIXME
    def read_wchars(self, len, null_terminated=False):
        data = self.read(len * 2)
        
        # String is null terminated, remove the null char
        if null_terminated:
            data = data[:-2]
        if self._endianess == BIG_ENDIAN:
            return unicode(data, "UTF-16-BE")
        else:
            return unicode(data, "UTF-16-LE")
    
    def read_subsegment(self, length):
        return StringParser(self.read(length))
    
    def convert_uintvar(self, data, endianess=None):
        """ Convert a string of variable length to an integer """
        
        # using struct.unpack is twice as fast as this function, however
        # it's not flexible enough
        
        if endianess is None:
            endianess = self._endianess
            
        if endianess == BIG_ENDIAN:
            data = data[::-1]
            
        mask = 0
        value = ord(data[0])
        for octet in data[1:]:
            mask += 8
            value += (ord(octet) << mask)

        return value

    # ASF Specification requires the guid type, which is 128 bits aka 16 bytes
    def read_guid(self):
        # See http://www.ietf.org/rfc/rfc4122.txt for specification
        # The version number is in the most significant 4 bits of the time
        # stamp (bits 4 through 7 of the time_hi_and_version field).

        # retrieve version        
        position = self.tell()
        self.seek(position + 6)
        version = self.read_uint16() >> 12
        self.seek(position)
        
        #print repr([hex(ord(x)) for x in self.read(16)])
        
        self.seek(position)
        
        time_low = self.read_uint32() 
        time_mid = self.read_uint16()
        time_hi  = self.read_uint16()
        clock_seq_hi    = self.read_uint8()
        clock_seq_low   = self.read_uint8()
        node            = self.read(6)
        
        #print "uuid version = %d - %X" % (version, time_low)
        if version == 1:
            node = self.convert_uintvar(node, BIG_ENDIAN)
        else:
            node = self.convert_uintvar(node, BIG_ENDIAN)
        
        return "%08X-%04X-%04X-%X%X-%012X" % (time_low,
                                            time_mid,
                                            time_hi,
                                            clock_seq_hi,
                                            clock_seq_low,
                                            node)
                                     


    # Used in ASF and AVI parser, contains audio information
    class WAVEFORMATEX(object):
        codec_ids = {
            0x2000:     "AC3",
            0x161:      "WMA2",
            0x50:       "MP2",
            0x55:       "MP3",
            0x1:        "PCM",
            'unknown':  "???",
        }
        
        def __repr__(self):
            buffer  = "WAVEFORMATEX structure: \n"
            buffer += " %-35s : %s\n" % ("Codec ID / Format Tag", self.codec_id)
            buffer += " %-35s : %s\n" % ("Number of Channels", self.channels)
            buffer += " %-35s : %s\n" % ("Samples Per Second", self.sample_rate)
            buffer += " %-35s : %s\n" % ("Average Number of Bytes Per Second", self.bit_rate)
            buffer += " %-35s : %s\n" % ("Block Alignment", self.block_alignment)
            buffer += " %-35s : %s\n" % ("Bits Per Sample", self.bits_per_sample)
            buffer += " %-35s : %s\n" % ("Codec Specific Data Size",self.codec_size)
            buffer += " %-35s : %s\n" % ("Codec Specific Data", repr(self.codec_data))
            
            return buffer            
    
    
    def read_waveformatex(self):
        
        obj = self.WAVEFORMATEX()
        
        obj.codec_id = self.read_uint16()
        obj.channels = self.read_uint16()
        obj.sample_rate = self.read_uint32()
        obj.bit_rate = self.read_uint32()
        obj.block_alignment = self.read_uint16()
        obj.bits_per_sample = self.read_uint16()
        obj.codec_size = self.read_uint16()
        obj.codec_data = self.read_subsegment(obj.codec_size)
        
        return obj


    class BITMAPINFOHEADER(object):
        def __repr__(self):
            buffer  = "BITMAPINFOHEADER structure: \n"
            buffer += " %-35s : %s\n" % ("Format Data Size", self.format_data_size)
            buffer += " %-35s : %s\n" % ("Image Width", self.image_width)
            buffer += " %-35s : %s\n" % ("Image Height", self.image_height)
            buffer += " %-35s : %s\n" % ("Reserved", self.reserved)
            buffer += " %-35s : %s\n" % ("Bits Per Pixel Count", self.bpp)
            buffer += " %-35s : %s\n" % ("Compression ID", self.compression_id)
            buffer += " %-35s : %s\n" % ("Image Size", self.image_size)
            buffer += " %-35s : %s\n" % ("Horizontal Pixels Per Meter", self.h_pixels_meter)
            buffer += " %-35s : %s\n" % ("Vertical Pixels Per Meter", self.v_pixels_meter)
            buffer += " %-35s : %s\n" % ("Colors Used Count", self.colors)
            buffer += " %-35s : %s\n" % ("Important Colors Count", self.important_colors)
            buffer += " %-35s : %s\n" % ("Codec Specific Data", self.codec_data)

            return buffer
    
    def read_bitmapinfoheader(self):
        obj = self.BITMAPINFOHEADER()
        
        obj.format_data_size    = self.read_uint32()
        obj.image_width         = self.read_uint32()
        obj.image_height        = self.read_uint32()
        obj.reserved            = self.read_uint16()
        obj.bpp                 = self.read_uint16()
        obj.compression_id      = self.read(4)
        obj.image_size          = self.read_uint32()
        obj.h_pixels_meter      = self.read_uint32()
        obj.v_pixels_meter      = self.read_uint32()
        obj.colors              = self.read_uint32()
        obj.important_colors    = self.read_uint32()
        obj.codec_data          = self.read_subsegment(obj.format_data_size -
                                                       40)
        
        return obj
    
    
class BaseParser(object):
    pass

class File(BinaryReader):
    
    def __init__(self, filename, endianess):
        BinaryReader.__init__(self)
        self._offset = 0
        self._fileobj = open(filename, 'rb')
        
        self.set_endianess(endianess)

    def __del__(self):
        self._fileobj.close()
        
    # Override
    def validate(self):
        return False

    def read(self, bytes):
        self._offset += bytes
        return self._fileobj.read(bytes)
    
    def seek(self, offset):
        self._offset = offset
        self._fileobj.seek(offset)
    
    def skip(self, bytes):
        self.seek(self._offset + bytes)

    
    def tell(self):
        return self._fileobj.tell()


#class StringParser(StringIO.StringIO, BinaryReader):
#    def __init__(self, data):
#        BinaryReader.__init__(self)
#        StringIO.StringIO.__init__(self, data)


# cStringIO is faster but can't be subclassed, but it performs 33% faster:
# Using this object, 100 times parsing a file is 0.220 cpu seconds vs
# using StringIO.StringIO's 0.340 cpu seconds.
class StringParser(BinaryReader):
    __slots__ = ['_data']

    def __init__(self, data):
        BinaryReader.__init__(self)
        self._data = cStringIO.StringIO(data)
    
    def read(self, length):
        return self._data.read(length)

    def tell(self):
        return self._data.tell()
    
    def seek(self, position):
        return self._data.seek(position)
    
    def close(self):
        return self._data.close()


