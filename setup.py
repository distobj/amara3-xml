#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Note: careful not to conflate install_requires with requirements.txt

https://packaging.python.org/discussions/install-requires-vs-requirements/

Reluctantly use setuptools to get install_requires & long_description_content_type
'''

import sys
from setuptools import setup, Extension
#from distutils.core import setup, Extension
#from distutils.core import Extension
import sys

#download_url = 'https://github.com/uogbuji/amara3-xml/tarball/v' + __version__,
PROJECT_NAME = 'amara3.xml' #'amara3-xml'
PROJECT_DESCRIPTION = 'Amara3 project, which offers a variety of data processing tools. This module adds the MicroXML support, and adaptation to classic XML.'
PROJECT_LICENSE = 'License :: OSI Approved :: Apache Software License'
PROJECT_AUTHOR = 'Uche Ogbuji'
PROJECT_AUTHOR_EMAIL = 'uche@ogbuji.net'
PROJECT_URL = 'https://github.com/uogbuji/amara3-xml'
PACKAGE_DIR = {'amara3': 'pylib'}
PACKAGES = [
    'amara3',
    'amara3.uxml',
    'amara3.uxml.uxpath'
]
SCRIPTS = [
    'exec/microx'
]

CORE_REQUIREMENTS = [
    'amara3.iri',
    'nameparser',
    'pytest',
    'ply',
]

# From http://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Development Status :: 4 - Beta",
    #"Environment :: Other Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Internet :: WWW/HTTP",
]

KEYWORDS=['xml', 'web', 'data']

version_file = 'pylib/version.py'
exec(compile(open(version_file, "rb").read(), version_file, 'exec'), globals(), locals())
__version__ = '.'.join(version_info)

#If you run into a prob with missing limits.h on Ubuntu/Mint, try:
#sudo apt-get install libc6-dev
cxmlstring = Extension('amara3.cmodules.cxmlstring', sources=['clib/xmlstring.c'], include_dirs=['clib/'])

LONGDESC = '''amara3-xml

A data processing library built on Python 3 and `MicroXML`_. This module
adds the MicroXML support, and adaptation to classic XML. Requires Python 3.4+

## Use

Amara is focused on [MicroXML](http://www.w3.org/community/microxml/), rather than full XML.
However because most of the XML-like data you’ll be dealing with is XML
1.0, Amara provides capabilities to parse legacy XML and reduce it to
MicroXML. In many cases the biggest implication of this is that
namespace information is stripped. As long as you know what you’re doing
you can get pretty far by ignoring this, but make sure you know what
you’re doing.

    from amara3.uxml import xml

    MONTY_XML = """<monty xmlns="urn:spam:ignored">
      <python spam="eggs">What do you mean "bleh"</python>
      <python ministry="abuse">But I was looking for argument</python>
    </monty>"""

    builder = xml.treebuilder()
    root = builder.parse(MONTY_XML)
    print(root.xml_name) #"monty"
    child = next(root.xml_children)
    print(child) #First text node: "\n  "
    child = next(root.xml_children)
    print(child.xml_value) #"What do you mean \"bleh\""
    print(child.xml_attributes["spam"]) #"eggs"

There are some utilities to make this a bit easier as well.

    from amara3.uxml import xml
    from amara3.uxml.treeutil import *

    MONTY_XML = """<monty xmlns="urn:spam:ignored">
      <python spam="eggs">What do you mean "bleh"</python>
      <python ministry="abuse">But I was looking for argument</python>
    </monty>"""

    builder = xml.treebuilder()
    root = builder.parse(MONTY_XML)
    py1 = next(select_name(root, "python"))
    print(py1.xml_value) #"What do you mean \"bleh\""
    py2 = next(select_attribute(root, "ministry", "abuse"))
    print(py2.xml_value) #"But I was looking for argument"

## Experimental MicroXML parser

For this parser the input truly must be MicroXML. Basics:

    >>> from amara3.uxml.parser import parse
    >>> events = parse('<hello><bold>world</bold></hello>')
    >>> for ev in events: print(ev)
    ...
    (<event.start_element: 1>, 'hello', {}, [])
    (<event.start_element: 1>, 'bold', {}, ['hello'])
    (<event.characters: 3>, 'world')
    (<event.end_element: 2>, 'bold', ['hello'])
    (<event.end_element: 2>, 'hello', [])
    >>>

Or…And now for something completely different!…Incremental parsing.

    >>> from amara3.uxml.parser import parsefrags
    >>> events = parsefrags(['<hello', '><bold>world</bold></hello>'])
    >>> for ev in events: print(ev)
    ...
    (<event.start_element: 1>, 'hello', {}, [])
    (<event.start_element: 1>, 'bold', {}, ['hello'])
    (<event.characters: 3>, 'world')
    (<event.end_element: 2>, 'bold

----

Author: [Uche Ogbuji](http://uche.ogbuji.net) <uche@ogbuji.net>
'''

LONGDESC_CTYPE = 'text/markdown',

setup(
    name=PROJECT_NAME,
    version=__version__,
    description=PROJECT_DESCRIPTION,
    license=PROJECT_LICENSE,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_AUTHOR_EMAIL,
    #maintainer=PROJECT_MAINTAINER,
    #maintainer_email=PROJECT_MAINTAINER_EMAIL,
    url=PROJECT_URL,
    package_dir=PACKAGE_DIR,
    packages=PACKAGES,
    scripts=SCRIPTS,
    ext_modules = [cxmlstring],
    install_requires=CORE_REQUIREMENTS,
    classifiers=CLASSIFIERS,
    long_description=LONGDESC,
    long_description_content_type=LONGDESC_CTYPE,
    keywords=KEYWORDS,
)

#long_description = LONGDESC

