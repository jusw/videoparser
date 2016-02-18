# VideoParser #
Python parser to retrieve header information from various video formats.

**It is still in early development, some values for formats are missing or could be incorrect**


## Supported video formats ##
  * ASF/WMV
  * AVI
  * Matroska
  * QuickTime
  * RealMedia


## Usage ##
```
import videoparser

parser = videoparser.VideoParser()
print parser.parse_file(<filename>)
```


## Download ##
http://pypi.python.org/pypi/videoparser/