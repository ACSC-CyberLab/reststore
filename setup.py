#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup

import re
import platform
import os
import sys


install_requires = ["bottle>=0.11",
                    "requests>=1.1.0",
                    "pyyaml>=0.0"]

def load_version(filename='./filestore/version.py'):
    """Parse a __version__ number from a source file"""
    with open(filename) as source:
        text = source.read()
        match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", text)
        if not match:
            msg = "Unable to find version number in {}".format(filename)
            raise RuntimeError(msg)
        version = match.group(1)
        return version

setup(
    name="filestore",
    version=load_version(),
    packages=["filestore"],
    zip_safe=False,
    author="Michael Dorman",
    author_email="mjdorma+filestore@gmail.com",
    url="",
    description="Light weight file store with a RESTful web API.",
    long_description=open('README.rst').read(),
    license="Apache Software Licence",
    install_requires = install_requires,
    entry_points={
        'console_scripts': [
            'filestore = filestore.cli:entry',
            ]
    },
    platforms=['cygwin', 'win', 'linux'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Security',
        'Topic :: System :: Monitoring'
    ],
    test_suite="tests",
    tests_require=[]
)
