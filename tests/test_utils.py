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

import six
import plotextractor


def test_get_image_location_ok(tmpdir):
    image = "img/img.png"
    path = six.text_type(tmpdir.mkdir('img').join("img.png"))
    image_list = [path]

    assert path == plotextractor.output_utils.get_image_location(
        image,
        six.text_type(tmpdir),
        image_list
    )


def test_get_image_location_missing_subfolder(tmpdir):
    image = "img.png"
    path = tmpdir.mkdir('fig').join(image)
    path.write('test')
    filepath = six.text_type(path)
    image_list = [filepath]

    assert filepath == plotextractor.output_utils.get_image_location(
        image,
        six.text_type(tmpdir),
        image_list
    )


def test_get_image_location_not_ok(tmpdir):
    image = "notanimage"
    path = six.text_type(tmpdir.mkdir('images').join("some.img"))
    image_list = [path]

    assert plotextractor.output_utils.get_image_location(
        image,
        six.text_type(tmpdir),
        image_list
    ) is None


def test_get_image_location_includegraphics(tmpdir):
    image = "\\includegraphics{some}"
    path = six.text_type(tmpdir.join("some.png"))
    image_list = [path]

    assert path == plotextractor.output_utils.get_image_location(
        image,
        six.text_type(tmpdir),
        image_list
    )
