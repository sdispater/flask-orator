# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

here = os.path.dirname(__file__)

def get_version():
    with open(os.path.join(here, 'flask_orator/version.py')) as f:
        variables = {}
        exec(f.read(), variables)

        version = variables.get('VERSION')
        if version:
            return version

    raise RuntimeError('No version info found.')


__version__ = get_version()

with open(os.path.join(here, 'requirements.txt')) as f:
    requirements = f.readlines()

setup(
    name='flask-orator',
    license='MIT',
    version=__version__,
    description='Adds Orator support to your Flask application',
    long_description=open('README.rst').read(),
    author='Sébastien Eustace',
    author_email='sebastien.eustace@gmail.com',
    url='https://github.com/sdispater/flask-orator',
    download_url='https://github.com/sdispater/flask-orator/archive/%s.tar.gz' % __version__,
    packages=find_packages(),
    install_requires=requirements,
    tests_require=['pytest', 'mock'],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
