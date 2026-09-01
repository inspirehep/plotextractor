# -*- coding: utf-8 -*-
#
# This file is part of plotextractor.
# Copyright (C) 2010, 2011, 2015, 2016, 2020 CERN.
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

import ntpath
import os
import tarfile
import re
import sys
import subprocess
from time import time
from pdf2image import convert_from_path

import magic
from PIL import Image

from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError,
)
from .errors import InvalidTarball
from .output_utils import get_converted_image_name, get_image_location

MAX_BYTES = 5 * 1024 * 1024  # 5 MB cap


def compress_png(path, image_format):
    """
    Runs compress_png on the given file.
    If it is larger than 5MB, it will be compressed to a PNG
    with a palette of 256 colors.
    This approximation based on tests, converts a 15mb png to a 4.5mb png
    Returns the path on success, or None if compression failed.
    """
    size = os.path.getsize(path)

    if size > MAX_BYTES:
        try:
            img = Image.open(path)
            pal = img.convert("P", palette=Image.ADAPTIVE, colors=256)
            pal.save(path, format=image_format, optimize=True)
        except Exception:
            return None
    return path


def is_within_directory(directory, target):
    """Return True if ``target`` is ``directory`` itself or below it."""
    try:
        relative_path = os.path.relpath(target, directory)
    except ValueError:
        return False
    return relative_path != os.pardir and not relative_path.startswith(
        os.pardir + os.sep
    )


def traverses_on_windows(name):
    """Return True if ``name`` escapes when the path is read by Windows.

    Backslash is an ordinary filename character on POSIX, so a member named
    ``..\\..\\etc\\passwd`` extracts harmlessly into the destination here.
    It becomes a traversal the moment the extracted tree is opened on
    Windows or served over SMB, so the check runs on every platform. No
    legitimate source file traverses this way, so it costs nothing.
    """
    if ntpath.isabs(name) or ntpath.splitdrive(name)[0]:
        return True
    normalized = ntpath.normpath(name)
    return normalized == ntpath.pardir or normalized.startswith(
        ntpath.pardir + ntpath.sep
    )


def safe_members(members, output_directory):
    """Return the members that are safe to extract into ``output_directory``.

    Anything else is skipped rather than aborting the archive, which is how
    the rest of this module already treats individual files it cannot
    handle.
    """
    destination = os.path.realpath(output_directory)
    safe = []
    for member in members:
        # Symlinks, hard links and device nodes can all redirect a later
        # write outside the destination.
        if not (member.isfile() or member.isdir()):
            continue
        if traverses_on_windows(member.name):
            continue
        # realpath resolves ".." and any symlink already in the destination.
        target = os.path.realpath(os.path.join(destination, member.name))
        if not is_within_directory(destination, target):
            continue
        safe.append(member)
    return safe


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
    # set mtimes of members to now
    epochsecs = int(time())
    members = safe_members(tarball.getmembers(), output_directory)
    for member in members:
        member.mtime = epochsecs
    tarball.extractall(output_directory, members=members)

    file_list = []

    for extracted_file in (member.name for member in members):
        if extracted_file == "":
            break
        if extracted_file.startswith("./"):
            extracted_file = extracted_file[2:]
        # ensure we are actually looking at the right file
        extracted_file = os.path.join(output_directory, extracted_file)

        # Add to full list of extracted files
        file_list.append(extracted_file)

    return file_list


def detect_images_and_tex(
    file_list, allowed_image_types=("eps", "png", "ps", "jpg", "pdf"), timeout=20
):
    """Detect from a list of files which are TeX or images.

    :param: file_list (list): list of absolute file paths
    :param: allowed_image_types (list): list of allows image formats
    :param: timeout (int): the timeout value on shell commands.

    :return: (image_list, tex_file) (([string, string, ...], string)):
        list of images in the tarball and the name of the TeX file in the
        tarball.
    """
    tex_file_extension = "tex"

    image_list = []
    might_be_tex = []

    for extracted_file in file_list:
        # Ignore directories and hidden (metadata) files
        if re.search(r"[\uD800-\uDFFF]", extracted_file) and sys.version_info[0] == 3:
            # Illegal file path/name
            continue
        if os.path.isdir(extracted_file) or os.path.basename(extracted_file).startswith(
            "."
        ):
            continue

        magic_str = magic.from_file(extracted_file, mime=True)

        if magic_str == "application/x-tex":
            might_be_tex.append(extracted_file)
        elif magic_str.startswith("image/") or magic_str == "application/postscript":
            image_list.append(extracted_file)

        # If neither, maybe it is TeX or an image anyway, otherwise,
        # we don't care.
        else:
            _, dotted_file_extension = os.path.splitext(extracted_file)
            file_extension = dotted_file_extension[1:]

            if file_extension == tex_file_extension:
                might_be_tex.append(extracted_file)
            elif file_extension in allowed_image_types:
                image_list.append(extracted_file)

    return image_list, might_be_tex


def convert_images(image_list, image_format="png", timeout=20):
    """Convert images from list of images to given format, if needed.

    Figure out the types of the images that were extracted from
    the tarball and determine how to convert them into PNG.

    :param: image_list ([string, string, ...]): the list of image files
        extracted from the tarball in step 1
    :param: image_format (string): which image format to convert to.
        (PNG by default)
    :param: timeout (int): the timeout value on shell commands.

    :return: image_mapping ({new_image: original_image, ...]): The mapping of
        image files when all have been converted to PNG format.
    """
    image_mapping = {}
    for image_file in image_list:
        if os.path.isdir(image_file):
            continue

        if not os.path.exists(image_file):
            continue

        if magic.from_file(image_file, mime=True) == "image/png":
            # Already PNG - Compress if needed
            image_file_path = compress_png(image_file, image_format)
            if image_file_path:
                image_mapping[image_file] = image_file
            else:
                # Skip if compression failed
                continue
        else:
            # we're just going to assume that Pillow can convert all
            # the image types that we may be faced with
            # for sure it can do EPS->PNG and JPG->PNG and PS->PNG
            # and PSTEX->PNG
            converted_image_file = get_converted_image_name(image_file)
            try:
                out_file = convert_image(image_file, converted_image_file, image_format)
            except (
                KeyError,
                IOError,
                Image.DecompressionBombError,
                PDFInfoNotInstalledError,
                PDFPageCountError,
                PDFSyntaxError,
                subprocess.CalledProcessError,
            ):
                # Too bad, cannot convert image format.
                continue
            if out_file and os.path.exists(out_file):
                image_mapping[out_file] = image_file

    return image_mapping


def convert_image(from_file, to_file, image_format):
    """Convert an image to given format."""
    if magic.from_file(from_file, mime=True) == "application/pdf":
        convert_from_path(
            from_file,
            dpi=100,
            output_folder=os.path.dirname(to_file),
            fmt=image_format,
            single_file=True,
            output_file=os.path.splitext(os.path.basename(to_file))[0],
        )
    else:
        Image.open(from_file).save(to_file, format=image_format)

    return compress_png(to_file, image_format)


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
    degrees = re.findall(r"(\bangle=-?[\d]+|\brotate=-?[\d]+)", line)

    if len(degrees) < 1:
        return False

    degrees = degrees[0].split("=")[-1].strip()

    if file_loc is None or file_loc == "ERROR" or not re.match("-*\\d+", degrees):
        return False

    if degrees:
        try:
            degrees = int(degrees)
        except (ValueError, TypeError):
            return False

        if not os.path.exists(file_loc):
            return False

        with Image.open(file_loc) as image:
            rotated = image.rotate(degrees)
            rotated.save(file_loc)
        return True
    return False
