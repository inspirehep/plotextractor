# -*- coding: utf-8 -*-
#
# This file is part of plotextractor.
# Copyright (C) 2015, 2016 CERN.
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


@pytest.fixture
def tarball_flat():
    """Return path to testdata with a flat file hierarchy."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '1508.03176v1.tar.gz')


@pytest.fixture
def tarball_rotation():
    """Return path to testdata with an image file with rotation."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '1508.03176v1.tar.gz')


@pytest.fixture
def tarball_no_tex():
    """Return path to testdata with no Tex files."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '1604.01763v2.tar.gz')


@pytest.fixture
def tarball_nested_folder():
    """Return path to testdata with images in a nested folder."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '1603.04438v1.tar.gz')


@pytest.fixture
def tarball_nested_folder_rotation():
    """Return path to testdata with images in a nested folder."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '1603.05617v1.tar.gz')


def test_process_api(tarball_flat):
    """Test simple API for extracting and linking files to TeX."""
    plots = plotextractor.process_tarball(tarball_flat)
    assert len(plots) == 22
    assert "label" in plots[0]
    assert plots[0]["label"]
    assert "url" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert plots[0]["captions"]
    assert "name" in plots[0]
    assert plots[0]["name"]


def test_process_api_with_context(tarball_flat):
    """Test simple API for extracting and linking files to TeX context."""
    plots = plotextractor.process_tarball(tarball_flat, context=True)
    assert len(plots) == 22
    assert "contexts" in plots[0]
    assert "label" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert "name" in plots[0]


def test_process_api_with_nested(tarball_nested_folder):
    """Test simple API for extracting and linking files to TeX context."""
    plots = plotextractor.process_tarball(tarball_nested_folder, context=True)
    assert len(plots) == 9
    assert "contexts" in plots[0]
    assert "label" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert "name" in plots[0]


def test_process_api_with_nested_rotation(tarball_nested_folder_rotation):
    """Test simple API for extracting and linking files to TeX context."""
    plots = plotextractor.process_tarball(tarball_nested_folder_rotation, context=True)
    assert len(plots) == 30
    assert "contexts" in plots[0]
    assert "label" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert "name" in plots[0]


def test_process_api_with_image_rotation(tarball_rotation):
    """Test simple API for extracting and linking files to TeX context."""
    plots = plotextractor.process_tarball(tarball_rotation)
    assert len(plots) == 22
    assert "label" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert "name" in plots[0]


def test_process_api_invalid_text():
    """Test simple API for extracting and linking files to TeX."""
    with tempfile.NamedTemporaryFile() as f:
        with pytest.raises(plotextractor.errors.InvalidTarball):
            plotextractor.process_tarball(f.name)


def test_process_api_no_tex(tarball_no_tex):
    """Test simple API for extracting and linking files to TeX."""
    with pytest.raises(plotextractor.errors.NoTexFilesFound):
        plotextractor.process_tarball(tarball_no_tex)
