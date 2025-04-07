# -*- coding: utf-8 -*-
#
# This file is part of plotextractor.
# Copyright (C) 2015 CERN.
#
# plotextractor is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# plotextractor is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with plotextractor; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Small library for extracting plots used in scholarly communication."""

import sys

from setuptools import setup

readme = open('README.md').read()

requirements = [
    'Wand>=0.4.1,<=0.5.9',
    'subprocess32>=3.2.6',
    'python-magic',
    'six>=1.7.2',
]

test_requirements = [
    'coverage>=4.0.0',
    'pytest>=2.8.0',
    'pytest-cov>=2.1.0',
    'pycodestyle>=2.8.0',
]

# Get the version string. Cannot be done with import!
setup(
    name='plotextractor',
    description=__doc__,
    long_description=readme,
    keywords='plots figures extraction TeX LaTeX',
    license='GPLv2',
    author='CERN',
    author_email='admin@inspirehep.net',
    url='https://github.com/inspirehep/plotextractor',
    packages=[
        'plotextractor',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements,
    extras_require={
        'tests': test_requirements
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',

    ],
    tests_require=test_requirements,
)
