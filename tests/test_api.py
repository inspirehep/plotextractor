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

from __future__ import absolute_import, print_function, unicode_literals

import os
import tempfile

import pytest
import plotextractor


def test_process_api():
    """Test simple API for extracting and linking files to TeX."""
    path_to_tarball = os.path.join(os.path.dirname(__file__),
                                   'data',
                                   '1508.03176v1.tar.gz')
    plots = plotextractor.process_tarball(path_to_tarball)
    assert len(plots) == 22
    assert "label" in plots[0]
    assert "url" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert "name" in plots[0]


def test_process_api_with_context():
    """Test simple API for extracting and linking files to TeX context."""
    path_to_tarball = os.path.join(os.path.dirname(__file__),
                                   'data',
                                   '1508.03176v1.tar.gz')
    plots = plotextractor.process_tarball(path_to_tarball, context=True)
    assert len(plots) == 22
    assert "contexts" in plots[0]
    assert "label" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert "name" in plots[0]


def test_process_api_invalid_text():
    """Test simple API for extracting and linking files to TeX."""
    with tempfile.NamedTemporaryFile() as f:
        with pytest.raises(plotextractor.errors.InvalidTarball):
            plotextractor.process_tarball(f.name)
