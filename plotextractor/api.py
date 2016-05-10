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

"""API for plotextractor utility."""

from __future__ import absolute_import, print_function

import os

from .extractor import (
    extract_captions,
    extract_context,
)
from .converter import convert_images, untar, detect_images_and_tex
from .output_utils import (
    prepare_image_data,
)
from .errors import NoTexFilesFound


def process_tarball(tarball, output_directory=None, context=False):
    """Process one tarball end-to-end.

    If output directory is given, the tarball will be extracted there.
    Otherwise, it will extract it in a folder next to the tarball file.

    The function returns a list of dictionaries:

    .. code-block:: python

        [{
            'url': '/path/to/tarball_files/d15-120f3d.png',
            'captions': ['The $\\rho^0$ meson properties: (a) Mass ...'],
            'name': 'd15-120f3d',
            'label': 'fig:mass'
        }, ... ]

    :param: tarball (string): the absolute location of the tarball we wish
        to process
    :param: output_directory (string): path of file processing and extraction
        (optional)
    :param: context: if True, also try to extract context where images are
        referenced in the text. (optional)
    :return: images(list): list of dictionaries for each image with captions.
    """
    if not output_directory:
        # No directory given, so we use the same path as the tarball
        output_directory = os.path.abspath("{0}_files".format(tarball))

    extracted_files_list = untar(tarball, output_directory)
    image_list, tex_files = detect_images_and_tex(extracted_files_list)

    if tex_files == [] or tex_files is None:
        raise NoTexFilesFound("No TeX files found in {0}".format(tarball))

    converted_image_mapping = convert_images(image_list)
    return map_images_in_tex(
        tex_files,
        converted_image_mapping,
        output_directory,
        context
    )


def map_images_in_tex(tex_files, image_mapping,
                      output_directory, context=False):
    """Return caption and context for image references found in TeX sources."""
    extracted_image_data = []
    for tex_file in tex_files:
        # Extract images, captions and labels based on tex file and images
        partly_extracted_image_data = extract_captions(
            tex_file,
            output_directory,
            image_mapping.keys()
        )
        if partly_extracted_image_data:
            # Convert to dict, add proper filepaths and do various cleaning
            cleaned_image_data = prepare_image_data(
                partly_extracted_image_data,
                output_directory,
                image_mapping,
            )
            if context:
                # Using prev. extracted info, get contexts for each image found
                extract_context(tex_file, cleaned_image_data)

            extracted_image_data.extend(cleaned_image_data)

    return extracted_image_data
