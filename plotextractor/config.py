# -*- coding: utf-8 -*-
#
# This file is part of plotextractor.
# Copyright (C) 2010, 2011, 2015 CERN.
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

# pylint: disable=C0301

"""Plotextractor configuration."""

from __future__ import absolute_import, print_function


# CFG_PLOTEXTRACTOR_DESY_BASE --
CFG_PLOTEXTRACTOR_DESY_BASE = 'http://www-library.desy.de/preparch/desy/'

# CFG_PLOTEXTRACTOR_DESY_PIECE --
CFG_PLOTEXTRACTOR_DESY_PIECE = '/desy'

CFG_PLOTEXTRACTOR_CONTEXT_WORD_LIMIT = 75

CFG_PLOTEXTRACTOR_CONTEXT_SENTENCE_LIMIT = 2

CFG_PLOTEXTRACTOR_CONTEXT_EXTRACT_LIMIT = 750

CFG_PLOTEXTRACTOR_DISALLOWED_TEX = [
    'begin', 'end', 'section', 'includegraphics', 'caption',
    'acknowledgements',
]
