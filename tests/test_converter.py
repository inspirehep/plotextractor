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

import magic
import os
import pkg_resources
from shutil import rmtree
from tempfile import mkdtemp

from plotextractor.converter import detect_images_and_tex, untar


def test_detect_images_and_tex_ignores_hidden_metadata_files():
    tarball_filename = pkg_resources.resource_filename(
        __name__, os.path.join('data', '1704.02281.tar.gz'))
    try:
        temporary_dir = mkdtemp()
        file_list = untar(tarball_filename, temporary_dir)
        image_files, _ = detect_images_and_tex(file_list)
        # Ensure image_list doesn't contain a hidden or metadata file
        for f in image_files:
            assert 'image' in magic.from_file(f).lower() \
                or 'eps' in magic.from_file(f).lower() \
                or 'Postscript' in magic.from_file(f)
    finally:
        rmtree(temporary_dir)
