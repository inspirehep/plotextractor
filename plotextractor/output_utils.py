# -*- coding: utf-8 -*-
#
# This file is part of plotextractor.
# Copyright (C) 2010, 2011, 2014, 2015, 2016 CERN.
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

from __future__ import absolute_import, print_function

import os
import re

from collections import OrderedDict


def find_open_and_close_braces(line_index, start, brace, lines):
    """
    Take the line where we want to start and the index where we want to start
    and find the first instance of matched open and close braces of the same
    type as brace in file file.

    :param: line (int): the index of the line we want to start searching at
    :param: start (int): the index in the line we want to start searching at
    :param: brace (string): one of the type of brace we are looking for ({, },
        [, or ])
    :param lines ([string, string, ...]): the array of lines in the file we
        are looking in.

    :return: (start, start_line, end, end_line): (int, int, int): the index
        of the start and end of whatever braces we are looking for, and the
        line number that the end is on (since it may be different than the line
        we started on)
    """

    if brace in ['[', ']']:
        open_brace = '['
        close_brace = ']'
    elif brace in ['{', '}']:
        open_brace = '{'
        close_brace = '}'
    elif brace in ['(', ')']:
        open_brace = '('
        close_brace = ')'
    else:
        # unacceptable brace type!
        return (-1, -1, -1, -1)

    open_braces = []
    line = lines[line_index]

    ret_open_index = line.find(open_brace, start)
    line_index_cpy = line_index
    # sometimes people don't put the braces on the same line
    # as the tag
    while ret_open_index == -1:
        line_index = line_index + 1
        if line_index >= len(lines):
            # failed to find open braces...
            return (0, line_index_cpy, 0, line_index_cpy)
        line = lines[line_index]
        ret_open_index = line.find(open_brace)

    open_braces.append(open_brace)

    ret_open_line = line_index

    open_index = ret_open_index
    close_index = ret_open_index

    while len(open_braces) > 0:
        if open_index == -1 and close_index == -1:
            # we hit the end of the line!  oh, noez!
            line_index = line_index + 1

            if line_index >= len(lines):
                # hanging braces!
                return (ret_open_index, ret_open_line,
                        ret_open_index, ret_open_line)

            line = lines[line_index]
            # to not skip things that are at the beginning of the line
            close_index = line.find(close_brace)
            open_index = line.find(open_brace)

        else:
            if close_index != -1:
                close_index = line.find(close_brace, close_index + 1)
            if open_index != -1:
                open_index = line.find(open_brace, open_index + 1)

        if close_index != -1:
            open_braces.pop()
            if len(open_braces) == 0 and \
                    (open_index > close_index or open_index == -1):
                break
        if open_index != -1:
            open_braces.append(open_brace)

    ret_close_index = close_index

    return (ret_open_index, ret_open_line, ret_close_index, line_index)


def assemble_caption(begin_line, begin_index, end_line, end_index, lines):
    """
    Take the caption of a picture and put it all together
    in a nice way.  If it spans multiple lines, put it on one line.  If it
    contains controlled characters, strip them out.  If it has tags we don't
    want to worry about, get rid of them, etc.

    :param: begin_line (int): the index of the line where the caption begins
    :param: begin_index (int): the index within the line where the caption
        begins
    :param: end_line (int): the index of the line where the caption ends
    :param: end_index (int): the index within the line where the caption ends
    :param: lines ([string, string, ...]): the line strings of the text

    :return: caption (string): the caption, formatted and pieced together
    """

    # stuff we don't like
    label_head = '\\label{'

    # reassemble that sucker
    if end_line > begin_line:
        # our caption spanned multiple lines
        caption = lines[begin_line][begin_index:]

        for included_line_index in range(begin_line + 1, end_line):
            caption = caption + ' ' + lines[included_line_index]

        caption = caption + ' ' + lines[end_line][:end_index]
        caption = caption.replace('\n', ' ')
        caption = caption.replace('  ', ' ')
    else:
        # it fit on one line
        caption = lines[begin_line][begin_index:end_index]

    # clean out a label tag, if there is one
    label_begin = caption.find(label_head)
    if label_begin > -1:
        # we know that our caption is only one line, so if there's a label
        # tag in it, it will be all on one line.  so we make up some args
        dummy_start, dummy_start_line, label_end, dummy_end = \
                find_open_and_close_braces(0, label_begin, '{', [caption])
        caption = caption[:label_begin] + caption[label_end + 1:]

    caption = caption.strip()

    if len(caption) > 1 and caption[0] == '{' and caption[-1] == '}':
        caption = caption[1:-1]

    return caption


def prepare_image_data(extracted_image_data, output_directory,
                       image_mapping):
    """Prepare and clean image-data from duplicates and other garbage.

    :param: extracted_image_data ([(string, string, list, list) ...],
        ...])): the images and their captions + contexts, ordered
    :param: tex_file (string): the location of the TeX (used for finding the
        associated images; the TeX is assumed to be in the same directory
        as the converted images)
    :param: image_list ([string, string, ...]): a list of the converted
        image file names
    :return extracted_image_data ([(string, string, list, list) ...],
        ...])) again the list of image data cleaned for output
    """
    img_list = OrderedDict()
    for image, caption, label in extracted_image_data:
        if not image or image == 'ERROR':
            continue
        image_location = get_image_location(
            image,
            output_directory,
            image_mapping.keys()
        )

        if not image_location or not os.path.exists(image_location) or \
                len(image_location) < 3:
            continue

        image_location = os.path.normpath(image_location)
        if image_location in img_list:
            if caption not in img_list[image_location]['captions']:
                img_list[image_location]['captions'].append(caption)
        else:
            img_list[image_location] = dict(
                url=image_location,
                original_url=image_mapping[image_location],
                captions=[caption],
                label=label,
                name=get_name_from_path(image_location, output_directory)
            )
    return img_list.values()


def get_image_location(image, sdir, image_list, recurred=False):
    """Take a raw image name + directory and return the location of image.

    :param: image (string): the name of the raw image from the TeX
    :param: sdir (string): the directory where everything was unzipped to
    :param: image_list ([string, string, ...]): the list of images that
        were extracted from the tarball and possibly converted

    :return: converted_image (string): the full path to the (possibly
        converted) image file
    """
    if isinstance(image, list):
        # image is a list, not good
        return None

    image = image.encode('utf-8', 'ignore')
    image = image.strip()

    figure_or_file = '(figure=|file=)'
    figure_or_file_in_image = re.findall(figure_or_file, image)
    if len(figure_or_file_in_image) > 0:
        image = image.replace(figure_or_file_in_image[0], '')

    includegraphics = r'\\includegraphics{(.+)}'
    includegraphics_in_image = re.findall(includegraphics, image)
    if len(includegraphics_in_image) > 0:
        image = includegraphics_in_image[0]

    image = image.strip()

    some_kind_of_tag = '\\\\\\w+ '

    if image.startswith('./'):
        image = image[2:]
    if re.match(some_kind_of_tag, image):
        image = image[len(image.split(' ')[0]) + 1:]
    if image.startswith('='):
        image = image[1:]

    if len(image) == 1:
        return None

    image = image.strip()
    converted_image_should_be = get_converted_image_name(image)

    if image_list is None:
        image_list = os.listdir(sdir)

    for png_image in image_list:
        png_image_rel = os.path.relpath(png_image, start=sdir)
        if converted_image_should_be == png_image_rel:
            return png_image

    # maybe it's in a subfolder (TeX just understands that)
    for prefix in ['eps', 'fig', 'figs', 'figures', 'figs', 'images']:
        if os.path.isdir(os.path.join(sdir, prefix)):
            image_list = os.listdir(os.path.join(sdir, prefix))
            for png_image in image_list:
                if converted_image_should_be == png_image:
                    return os.path.join(sdir, prefix, png_image)

    # maybe it is actually just loose.
    for png_image in os.listdir(sdir):
        if os.path.split(converted_image_should_be)[-1] == png_image:
            return converted_image_should_be
        if os.path.isdir(os.path.join(sdir, png_image)):
            # try that, too!  we just do two levels, because that's all that's
            # reasonable..
            sub_dir = os.path.join(sdir, png_image)
            for sub_dir_file in os.listdir(sub_dir):
                if os.path.split(converted_image_should_be)[-1] == sub_dir_file:  # noqa
                    return os.path.join(sub_dir, converted_image_should_be)

    # maybe it's actually up a directory or two: this happens in nested
    # tarballs where the TeX is stored in a different directory from the images
    for png_image in os.listdir(os.path.split(sdir)[0]):
        if os.path.split(converted_image_should_be)[-1] == png_image:
            return converted_image_should_be
    for png_image in os.listdir(os.path.split(os.path.split(sdir)[0])[0]):
        if os.path.split(converted_image_should_be)[-1] == png_image:
            return converted_image_should_be

    if recurred:
        return None

    # agh, this calls for drastic measures
    for piece in image.split(' '):
        res = get_image_location(piece, sdir, image_list, recurred=True)
        if res is not None:
            return res

    for piece in image.split(','):
        res = get_image_location(piece, sdir, image_list, recurred=True)
        if res is not None:
            return res

    for piece in image.split('='):
        res = get_image_location(piece, sdir, image_list, recurred=True)
        if res is not None:
            return res

    return None


def get_converted_image_name(image):
    """Return the name of the image after it has been converted to png format.

    Strips off the old extension.

    :param: image (string): The fullpath of the image before conversion

    :return: converted_image (string): the fullpath of the image after convert
    """
    png_extension = '.png'

    if image[(0 - len(png_extension)):] == png_extension:
        # it already ends in png!  we're golden
        return image

    img_dir = os.path.split(image)[0]
    image = os.path.split(image)[-1]

    # cut off the old extension
    if len(image.split('.')) > 1:
        old_extension = '.' + image.split('.')[-1]
        converted_image = image[:(0 - len(old_extension))] + png_extension
    else:
        # no extension... damn
        converted_image = image + png_extension

    return os.path.join(img_dir, converted_image)


def get_tex_location(new_tex_name, current_tex_name, recurred=False):
    """
    Takes the name of a TeX file and attempts to match it to an actual file
    in the tarball.

    :param: new_tex_name (string): the name of the TeX file to find
    :param: current_tex_name (string): the location of the TeX file where we
        found the reference

    :return: tex_location (string): the location of the other TeX file on
        disk or None if it is not found
    """
    new_tex_name = str(new_tex_name)
    current_tex_name = str(current_tex_name)

    tex_location = None

    current_dir = os.path.split(current_tex_name)[0]

    some_kind_of_tag = '\\\\\\w+ '

    new_tex_name = new_tex_name.strip()
    if new_tex_name.startswith('input'):
        new_tex_name = new_tex_name[len('input'):]
    if re.match(some_kind_of_tag, new_tex_name):
        new_tex_name = new_tex_name[len(new_tex_name.split(' ')[0]) + 1:]
    if new_tex_name.startswith('./'):
        new_tex_name = new_tex_name[2:]
    if len(new_tex_name) == 0:
        return None
    new_tex_name = new_tex_name.strip()

    new_tex_file = os.path.split(new_tex_name)[-1]
    new_tex_folder = os.path.split(new_tex_name)[0]
    if new_tex_folder == new_tex_file:
        new_tex_folder = ''

    # could be in the current directory
    for any_file in os.listdir(current_dir):
        if any_file == new_tex_file:
            return os.path.join(current_dir, new_tex_file)

    # could be in a subfolder of the current directory
    if os.path.isdir(os.path.join(current_dir, new_tex_folder)):
        for any_file in os.listdir(os.path.join(current_dir, new_tex_folder)):
            if any_file == new_tex_file:
                return os.path.join(os.path.join(current_dir, new_tex_folder),
                                    new_tex_file)

    # could be in a subfolder of a higher directory
    one_dir_up = os.path.join(os.path.split(current_dir)[0], new_tex_folder)
    if os.path.isdir(one_dir_up):
        for any_file in os.listdir(one_dir_up):
            if any_file == new_tex_file:
                return os.path.join(one_dir_up, new_tex_file)

    two_dirs_up = os.path.join(os.path.split(os.path.split(current_dir)[0])[0],
                               new_tex_folder)
    if os.path.isdir(two_dirs_up):
        for any_file in os.listdir(two_dirs_up):
            if any_file == new_tex_file:
                return os.path.join(two_dirs_up, new_tex_file)

    if tex_location is None and not recurred:
        return get_tex_location(new_tex_name + '.tex', current_tex_name,
                                recurred=True)

    return tex_location


def get_name_from_path(full_path, root_path):
    """Create a filename by merging path after root directory."""
    relative_image_path = os.path.relpath(full_path, root_path)
    return "_".join(relative_image_path.split('.')[:-1]).replace('/', '_')\
        .replace(';', '').replace(':', '')
