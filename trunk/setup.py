from setuptools import setup, find_packages
from videoparser.version import version

setup(
    name = "videoparser",
    version = version,
    packages = find_packages(),

    # metadata for upload to PyPI
    author = "Michael van Tellingen",
    author_email = "michaelvantellingen@gmail.com",
    description = "Python parser to retrieve header information from various video formats.",
    license = "2-clause BSD",
    keywords = "video header formats matroska avi asf quicktime realmedia",
    url = "http://videoparser.googlecode.com/",

)


