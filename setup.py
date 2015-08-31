#!/usr/bin/env python
import sys
from setuptools import setup, find_packages

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='cts2000',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['pyserial', 'flask', 'requests', 'simplejson'],
    zip_safe=False,
    author='Bumblebee',
    author_email='git@bumblebee.cc',
    url='https://github.com/bumblebeefr/pyCTS2000',
    license='GNU GENERAL PUBLIC LICENSE Version 3',
    entry_points={
        'console_scripts': [
            'cts2000-webapp=cts2000.webapp:main',
        ],
    },
    **extra
)
