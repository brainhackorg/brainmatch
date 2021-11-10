"""This file contains the parameters that are used to fill the settings in
brainmatch's `setup.py`, to provide brainmatch's top-level docstring, and to
build the docs.
"""

# brainmatch version information. An empty _version_extra corresponds to a
# full release. '.dev' as a _version_extra string means this is a development
# version
_version_major = 0
_version_minor = 1
_version_micro = 0
_version_extra = 'dev0'
# _version_extra = ''

# Format expected by setup.py and doc/conf.py: string of form "X.Y.Z"
__version__ = '%s.%s.%s.%s' % (_version_major,
                               _version_minor,
                               _version_micro,
                               _version_extra)

classifiers = ['Development Status :: 3 - Alpha',
               'Intended Audience :: Science/Research',
               'Programming Language :: Python :: 3',
               'Topic :: Scientific/Engineering',
               'Topic :: Scientific/Engineering :: Neuroimaging']

description = 'Brainhack event project to attendee matching tools.'

keywords = 'Event project requirement-contributor request matching toolkit'

# Main setup parameters
NAME = 'brainmatch'
MAINTAINER = 'brainhack'
MAINTAINER_EMAIL = ''
DESCRIPTION = description
URL = 'https://github.com/brainhackorg/brainmatch'
DOWNLOAD_URL = ''
BUG_TRACKER = 'https://github.com/brainhackorg/brainmatch/issues'
DOCUMENTATION = ''
SOURCE_CODE = 'https://github.com/brainhackorg/brainmatch'
LICENSE = ''
CLASSIFIERS = classifiers
KEYWORDS = keywords
AUTHOR = 'brainhack'
AUTHOR_EMAIL = 'brainhackorg@gmail.com'
PLATFORMS = ''
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
ISRELEASE = _version_extra == ''
VERSION = __version__
PROVIDES = ['brainmatch']
REQUIRES = ['pandas']
