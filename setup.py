# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'flask_orator/version.py')) as f:
        variables = {}
        exec(f.read(), variables)

        version = variables.get('VERSION')
        if version:
            return version

    raise RuntimeError('No version info found.')


__version__ = get_version()

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
    packages=['flask_orator'],
    install_requires=[
        'Flask>=0.10',
        'orator',
        'cleo'
    ],
    tests_require=['pytest', 'mock'],
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
