#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='reachy-otis',
    version='1.0.1',
    packages=find_packages(exclude=['tests']),

    install_requires=[
        'numpy',
        'reachy>=1.3',
        'matplotlib',
    ],

    author='Pollen Robotics',
    author_email='contact@pollen-robotics.com',
    url='https://github.com/pollen-robotics/otis',

    description='Otis: handwriting end-effector for Reachy.',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
