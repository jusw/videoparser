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


class VideoFile(object):
    def __init__(self):
        self._streams = {}
        self._format = ''
        
    def add_stream(self, stream, index=None):
        if index is None:
            index = len(self._streams) + 1
        self._streams[index] = stream
    
    def get_stream(self, stream_index):
        return self._streams.get(stream_index)
    
    def set_container(self, format):
        self._format = format
    
    def new_video_stream(self, index=None):
        stream = VideoStream()
        self.add_stream(stream, index)
        return stream
    
    def new_audio_stream(self, index=None):
        stream = AudioStream()
        self.add_stream(stream, index)
        return stream
    
    def __repr__(self):
        buf =   " Container format: %s\n" % self._format 
        buf +=  " Streams: \n"
        
        for stream_index in self._streams:
            buf += "   %d (%s) => %s\n" % (stream_index,
                                       self._streams[stream_index].type,
                                       repr(self._streams[stream_index])
                                       )
        
        return buf
        

class VideoStream(object):
    def __init__(self):
        self._duration = 0
        self._framerate = 0
        self._codec = ''
        self.type = 'Video'
        self._width = 0
        self._height = 0
        
    def set_width(self, width):
        self._width = width
    
    def set_height(self, height):
        self._height = height
    
    def set_codec(self, codec):
        self._codec = codec
    
    def set_framerate(self, framerate):
        self._framerate = framerate
        
    def set_duration(self, duration):
        self._duration = duration
        
    def set_bitrate(self, bitrate):
        pass
    
    def set_codec_name(self, name):
        self._codec_name = name
    
    def set_codec_description(self, description):
        self._codec_description = description
        
    def __repr__(self):
        return "codec: %s, length: %s, resolution: %dx%d, fps: %s" % (
            self._codec, self._duration / 60.0, self._width, self._height, self._framerate)

class AudioStream(object):
    def __init__(self):
        self._channels = 0
        self._codec = ''
        self._sample_rate = 0
        self._duration = 0
        self._bitrate = 0
        self.type = 'Audio'
        
    def set_channels(self, num):
        self._channels = num
    
    def set_codec(self, codec):
        self._codec = codec
    
    def set_sample_rate(self, rate):
        self._sample_rate = rate
    
    def set_bitrate(self, bitrate):
        self._bitrate = bitrate

    def set_duration(self, duration):
        self._duration = duration

    def __repr__(self):
        return "codec: %s, length: %s, channel: %d, sample rate: %d, bitrate: %s" % (
            self._codec, self._duration, self._channels, self._sample_rate, self._bitrate)


    

