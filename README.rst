..
    This file is part of plotextractor.
    Copyright (C) 2015, 2016 CERN.

    plotextractor is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    plotextractor is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with plotextractor; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.


===============
 plotextractor
===============

Small library for converting and mapping plots in TeX source used in scholarly communication.

* Free software: GPLv2
* Documentation: http://pythonhosted.org/plotextractor/

*Originally part of Invenio https://github.com/inveniosoftware/invenio.*

Installation
============

.. code-block:: shell

    pip install plotextractor


Usage
=====

.. code-block:: python

    from plotextractor import process_tarball
    plots = process_tarball("/path/to/tarball.tar.gz")
    print(plots[0])
    {
        'url': '/path/to/tarball.tar.gz_files/d15-120f3d.png',
        'captions': ['The $\\rho^0$ meson properties: (a) Mass ...']
        'name': 'd15-120f3d',
        'label': 'fig:mass'
    }


Known issues
============

If you experience frequent ``DelegateError`` errors you may need to update your version
of GhostScript.
