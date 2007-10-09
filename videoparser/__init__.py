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

# Python built-in modules
import sys

# Project modules
import videofile


__all__ = ['VideoParser']


parser_modules = ['asf', 'matroska', 'avi']

class VideoParser(object):
    def __init__(self):
        self.parsers = []
        
        self._import_parsers()
    
    def _import_parsers(self):
        
        # Import the parsers
        for module_filename in parser_modules:
            try:
                module = __import__("plugins." + module_filename, None, None,
                                    "plugins")
            except ImportError, err:
                print "Unable to open parser module '%s'" % module_filename 
                continue
        
            # Create parser object
            try:
                parser = module.Parser()
            except AttributeError, err:
                print "Invalid parser module: %s" % err
                continue
            
            self.parsers.append(parser)

    
    def parse_file(self, filename):
        video = videofile.VideoFile()
        
        # Parse the file
        for parser in self.parsers:
            
            # Check if this is the right parser for the file
            try:
                print "Trying to parse %s with %s" % (filename, parser)
                if parser.parse(filename, video):
                    print video
                    #print "OK"
                    break
            except AssertionError:
                continue


if __name__ == "__main__":
    video_parser = VideoParser()
    for filename in sys.argv[1:]:
        video_parser.parse_file(filename)
