#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='cts2000',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['pyserial'],
    zip_safe=False,
    author='Bumblebee',
    author_email='git@bumblebee.cc',
    url='https://github.com/bumblebeefr/pyCTS2000',
    license='GNU GENERAL PUBLIC LICENSE Version 3',
)
