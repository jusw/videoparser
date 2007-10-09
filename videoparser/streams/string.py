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

import streams.binary
import cStringIO



# cStringIO is faster but can't be subclassed, but it performs 33% faster:
# Using this object, 100 times parsing a file is 0.220 cpu seconds vs
# using StringIO.StringIO's 0.340 cpu seconds.
class StringStream(streams.binary.BinaryStream):
    __slots__ = ['_data', '_length']

    def __init__(self, data, endianess=0):
        streams.binary.BinaryStream.__init__(self)
        self._data = cStringIO.StringIO(data)
        self.set_endianess(endianess)
        
        self._length = len(data)
        
    def read(self, length):
        return self._data.read(length)

    def tell(self):
        return self._data.tell()
    
    def seek(self, position):
        return self._data.seek(position)
    
    def close(self):
        return self._data.close()

    def bytes_left(self):
        return self._data.tell() < self._length

