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
from plotextractor import process_tarball


@pytest.fixture
def tarball_flat():
    """Return path to testdata with a flat file hierarchy."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '1508.03176v1.tar.gz')


@pytest.fixture
def tarball_test_for_include():
    """Return path to testdata with include tags."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '2207.tar.gz')


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


@pytest.fixture
def tarball_utf():
    """Return path to testdata with images in a nested folder."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '2003.02673.tar.gz')

@pytest.fixture
def tarball_subfloat():
    """Return path to testdata with subfloats."""
    return os.path.join(os.path.dirname(__file__),
                        'data',
                        '2203.14536.tar.gz')


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


def test_process_api_preserves_ordering_of_figures_with_one_source_file(tarball_flat):
    plots = plotextractor.process_tarball(tarball_flat)
    expected = [
        'd15-120f1',
        'd15-120f2',
        'd15-120f3a',
        'd15-120f3b',
        'd15-120f3c',
        'd15-120f3d',
        'd15-120f4',
        'd15-120f5',
        'd15-120f6a',
        'd15-120f6b',
        'd15-120f6c',
        'd15-120f6d',
        'd15-120f6e',
        'd15-120f7',
        'd15-120f8',
        'd15-120f9',
        'd15-120f10',
        'd15-120f11',
        'd15-120f12a',
        'd15-120f12b',
        'd15-120f12c',
        'd15-120f13'
    ]
    labels = [plot['name'] for plot in plots]

    assert len(plots) == 22
    assert expected == labels


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


def test_process_api_with_subfloats(tarball_subfloat):
    """Test simple API for extracting and linking files to TeX context."""
    plots = plotextractor.process_tarball(tarball_subfloat)
    assert len(plots) == 24
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


def test_process_tarball_with_utf_folder(tarball_utf):
    """Tests tarball with utf - Shouldn't break"""
    temporary_dir = tempfile.mkdtemp()
    plots = process_tarball(
        tarball_utf,
        output_directory=temporary_dir
    )


def test_process_api_with_include(tarball_test_for_include):
    """Test simple API for including the plots for \include tag."""
    plots = plotextractor.process_tarball(tarball_test_for_include, context=True)
    assert len(plots) == 155
    assert "contexts" in plots[0]
    assert "label" in plots[0]
    assert "original_url" in plots[0]
    assert "captions" in plots[0]
    assert "name" in plots[0]
