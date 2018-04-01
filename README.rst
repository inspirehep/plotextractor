..
    This file is part of plotextractor.
    Copyright (C) 2015, 2016, 2018 CERN.

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

.. image:: https://travis-ci.org/inspirehep/plotextractor.svg?branch=master
    :target: https://travis-ci.org/inspirehep/plotextractor

.. image:: https://coveralls.io/repos/github/inspirehep/plotextractor/badge.svg?branch=master
    :target: https://coveralls.io/github/inspirehep/plotextractor?branch=master


About
=====

A small library for extracting plots used in scholarly communication.


Install
=======

.. code-block:: console

    $ pip install plotextractor


Usage
=====

To extract plots from a tarball:

.. code-block:: python

    >>> from plotextractor import process_tarball
    >>> plots = process_tarball('./1503.07589.tar.gz')
    >>> print(plots[0])
    {
        'captions': [
            u'Scans of twice the negative log-likelihood ratio $-2\\ln\\Lambda(\\mH)$ as functions of the Higgs boson mass \\mH\\ for the ATLAS and CMS combination of the \\hgg\\ (red), \\hZZllll\\ (blue), and combined (black) channels. The dashed curves show the results accounting for statistical uncertainties only, with all nuisance parameters associated with systematic uncertainties fixed to their best-fit values. The 1 and 2 standard deviation limits are indicated by the intersections of the horizontal lines at 1 and 4, respectively, with the log-likelihood scan curves.',
        ],
        'label': u'figure_LHC_combined_obs',
        'name': 'LHC_combined_obs_unblind_final',
        'original_url': './1503.07589.tar.gz_files/LHC_combined_obs_unblind_final.pdf',
        'url': './1503.07589.tar.gz_files/LHC_combined_obs_unblind_final.png',
    }


Notes
=====

If you experience frequent ``DelegateError`` errors you may need to update your version
of GhostScript.


License
=======

GPLv2
