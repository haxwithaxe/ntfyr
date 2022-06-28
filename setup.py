#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='ntfyr',
    version='0.1',
    description='A simple client for ntfy.sh.',
    author='haxwithaxe',
    author_email='spam@haxwithaxe.net',
    url='https://github.com/haxwithaxe/ntfyr',
    packages=['ntfyr'],
    license='License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    scripts=['scripts/ntfyr'],
)
