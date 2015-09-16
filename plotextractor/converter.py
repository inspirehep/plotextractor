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

"""Functions related to conversion and untarring."""

from __future__ import absolute_import, print_function, unicode_literals

import os
import tarfile
import re

from subprocess32 import check_output, TimeoutExpired
from wand.image import Image

from .errors import InvalidTarball
from .output_utils import get_converted_image_name, get_image_location


def untar(original_tarball, output_directory):
    """Untar given tarball file into directory.

    Here we decide if our file is actually a tarball, then
    we untar it and return a list of extracted files.

    :param: tarball (string): the name of the tar file from arXiv
    :param: output_directory (string): the directory to untar in

    :return: list of absolute file paths
    """
    if not tarfile.is_tarfile(original_tarball):
        raise InvalidTarball

    tarball = tarfile.open(original_tarball)
    tarball.extractall(output_directory)

    file_list = []

    for extracted_file in tarball.getnames():
        if extracted_file == '':
            break
        if extracted_file.startswith('./'):
            extracted_file = extracted_file[2:]
        # ensure we are actually looking at the right file
        extracted_file = os.path.join(output_directory, extracted_file)

        # Add to full list of extracted files
        file_list.append(extracted_file)

    return file_list


def detect_images_and_tex(
        file_list,
        allowed_image_types=('eps', 'png', 'ps', 'jpg', 'pdf'),
        timeout=20):
    """Detect from a list of files which are TeX or images.

    :param: file_list (list): list of absolute file paths
    :param: allowed_image_types (list): list of allows image formats
    :param: timeout (int): the timeout value on shell commands.

    :return: (image_list, tex_file) (([string, string, ...], string)):
        list of images in the tarball and the name of the TeX file in the
        tarball.
    """
    tex_output_contains = 'TeX'

    tex_file_extension = 'tex'
    image_output_contains = 'image'
    eps_output_contains = '- type eps'
    ps_output_contains = 'Postscript'
    image_list = []
    might_be_tex = []
    for extracted_file in file_list:
        try:
            cmd_out = check_output(['file', extracted_file], timeout=20)
        except TimeoutExpired:
            continue

        # is it TeX?
        if cmd_out.find(tex_output_contains) > -1:
            might_be_tex.append(extracted_file)

        # is it an image?
        elif cmd_out.lower().find(image_output_contains) > cmd_out.find(':') \
                or \
                cmd_out.lower().find(eps_output_contains) > cmd_out.find(':')\
                or \
                cmd_out.find(ps_output_contains) > cmd_out.find(':'):
            # we have "image" in the output, and it is not in the filename
            # i.e. filename.ext: blah blah image blah blah
            image_list.append(extracted_file)

        # if neither, maybe it is TeX or an image anyway, otherwise,
        # we don't care
        else:
            if extracted_file.split('.')[-1].lower() == tex_file_extension:
                # we might have tex source!
                might_be_tex.append(extracted_file)
            elif extracted_file.split('.')[-1] in allowed_image_types:
                # we might have an image!
                image_list.append(extracted_file)

    return image_list, might_be_tex


def convert_images(image_list, image_format="png", timeout=20):
    """Figure out the types of the images that were extracted from
    the tarball and determine how to convert them into PNG.

    :param: image_list ([string, string, ...]): the list of image files
        extracted from the tarball in step 1å
    :param: image_format (string): which image format to convert to.
        (PNG by default)
    :param: timeout (int): the timeout value on shell commands.

    :return: image_mapping ({new_image: original_image, ...]): The mapping of
        image files when all have been converted to PNG format.
    """
    png_output_contains = 'PNG image'
    image_mapping = {}
    for image_file in image_list:
        if os.path.isdir(image_file):
            continue

        cmd_out = check_output(['file', image_file], timeout=timeout)
        if cmd_out.find(png_output_contains) > -1:
            # Already PNG
            image_mapping[image_file] = image_file
        else:
            # we're just going to assume that ImageMagick can convert all
            # the image types that we may be faced with
            # for sure it can do EPS->PNG and JPG->PNG and PS->PNG
            # and PSTEX->PNG
            converted_image_file = get_converted_image_name(image_file)
            convert_image(image_file, converted_image_file, image_format)
            if os.path.exists(converted_image_file):
                image_mapping[converted_image_file] = image_file

    return image_mapping


def convert_image(from_file, to_file, image_format):
    """Convert an image to given format."""
    with Image(filename=from_file) as original:
        with original.convert(image_format) as converted:
            converted.save(filename=to_file)
    return to_file


def rotate_image(filename, line, sdir, image_list):
    """Rotate a image.

    Given a filename and a line, figure out what it is that the author
    wanted to do wrt changing the rotation of the image and convert the
    file so that this rotation is reflected in its presentation.

    :param: filename (string): the name of the file as specified in the TeX
    :param: line (string): the line where the rotate command was found

    :output: the image file rotated in accordance with the rotate command
    :return: True if something was rotated
    """
    file_loc = get_image_location(filename, sdir, image_list)
    degrees = re.findall('(angle=[-\\d]+|rotate=[-\\d]+)', line)

    if len(degrees) < 1:
        return False

    degrees = degrees[0].split('=')[-1].strip()

    if file_loc is None or file_loc == 'ERROR' or\
            not re.match('-*\\d+', degrees):
        return False

    with Image(filename=file_loc) as image:
        with image.clone() as rotated:
            rotated.rotate(degrees)
            rotated.save(filename=file_loc)
