# -*- coding: utf-8 -*-
#
# This file is part of plotextractor.
# Copyright (C) 2010, 2011, 2014, 2015 CERN.
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

"""Plot extractor extractor."""

from __future__ import absolute_import, print_function

import codecs
import os
import re

from .config import (
    CFG_PLOTEXTRACTOR_CONTEXT_WORD_LIMIT,
    CFG_PLOTEXTRACTOR_CONTEXT_SENTENCE_LIMIT,
    CFG_PLOTEXTRACTOR_CONTEXT_EXTRACT_LIMIT,
    CFG_PLOTEXTRACTOR_DISALLOWED_TEX,
)

from .output_utils import (
    assemble_caption,
    find_open_and_close_braces,
    get_tex_location,
)
from .converter import rotate_image


ARXIV_HEADER = 'arXiv:'
PLOTS_DIR = 'plots'

MAIN_CAPTION_OR_IMAGE = 0
SUB_CAPTION_OR_IMAGE = 1


def get_context(lines, backwards=False):
    """Get context.

    Given a relevant string from a TeX file, this function will extract text
    from it as far as it is deemed contextually relevant, either backwards or
    forwards in the text.
    The level of relevance allowed is configurable. When it reaches some
    point in the text that is determined to be out of scope from the current
    context, like text that is identified as a new paragraph, a complex TeX
    structure ('/begin', '/end', etc.) etc., it will return the previously
    allocated text.

    For use when extracting text with contextual value for an figure or plot.

    :param lines (string): string to examine
    :param reversed (bool): are we searching backwards?

    :return context (string): extracted context
    """
    tex_tag = re.compile(r".*\\(\w+).*")
    sentence = re.compile(r"(?<=[.?!])[\s]+(?=[A-Z])")
    context = []

    word_list = lines.split()
    if backwards:
        word_list.reverse()

    # For each word we do the following:
    #   1. Check if we have reached word limit
    #   2. If not, see if this is a TeX tag and see if its 'illegal'
    #   3. Otherwise, add word to context
    for word in word_list:
        if len(context) >= CFG_PLOTEXTRACTOR_CONTEXT_WORD_LIMIT:
            break
        match = tex_tag.match(word)
        if match and match.group(1) in CFG_PLOTEXTRACTOR_DISALLOWED_TEX:
            # TeX Construct matched, return
            if backwards:
                # When reversed we need to go back and
                # remove unwanted data within brackets
                temp_word = ""
                while len(context):
                    temp_word = context.pop()
                    if '}' in temp_word:
                        break
            break
        context.append(word)

    if backwards:
        context.reverse()
    text = " ".join(context)
    sentence_list = sentence.split(text)

    if backwards:
        sentence_list.reverse()

    if len(sentence_list) > CFG_PLOTEXTRACTOR_CONTEXT_SENTENCE_LIMIT:
        return " ".join(
            sentence_list[:CFG_PLOTEXTRACTOR_CONTEXT_SENTENCE_LIMIT])
    else:
        return " ".join(sentence_list)


def extract_context(tex_file, extracted_image_data):
    """Extract context.

    Given a .tex file and a label name, this function will extract the text
    before and after for all the references made to this label in the text.
    The number of characters to extract before and after is configurable.

    :param tex_file (list): path to .tex file
    :param extracted_image_data ([(string, string, list), ...]):
        a list of tuples of images matched to labels and captions from
        this document.

    :return extracted_image_data ([(string, string, list, list),
        (string, string, list, list),...)]: the same list, but now containing
        extracted contexts
    """
    if os.path.isdir(tex_file) or not os.path.exists(tex_file):
        return []

    lines = "".join(get_lines_from_file(tex_file))

    # Generate context for each image and its assoc. labels
    for data in extracted_image_data:
        context_list = []

        # Generate a list of index tuples for all matches
        indicies = [match.span()
                    for match in re.finditer(r"(\\(?:fig|ref)\{%s\})" %
                                             (re.escape(data['label']),),
                                             lines)]
        for startindex, endindex in indicies:
            # Retrive all lines before label until beginning of file
            i = startindex - CFG_PLOTEXTRACTOR_CONTEXT_EXTRACT_LIMIT
            if i < 0:
                text_before = lines[:startindex]
            else:
                text_before = lines[i:startindex]
            context_before = get_context(text_before, backwards=True)

            # Retrive all lines from label until end of file and get context
            i = endindex + CFG_PLOTEXTRACTOR_CONTEXT_EXTRACT_LIMIT
            text_after = lines[endindex:i]
            context_after = get_context(text_after)
            context_list.append(
                context_before + ' \\ref{' + data['label'] + '} ' +
                context_after
            )
        data['contexts'] = context_list


def extract_captions(tex_file, sdir, image_list, primary=True):
    """Extract captions.

    Take the TeX file and the list of images in the tarball (which all,
    presumably, are used in the TeX file) and figure out which captions
    in the text are associated with which images
    :param: lines (list): list of lines of the TeX file

    :param: tex_file (string): the name of the TeX file which mentions
        the images
    :param: sdir (string): path to current sub-directory
    :param: image_list (list): list of images in tarball
    :param: primary (bool): is this the primary call to extract_caption?

    :return: images_and_captions_and_labels ([(string, string, list),
        (string, string, list), ...]):
        a list of tuples representing the names of images and their
        corresponding figure labels from the TeX file
    """
    if os.path.isdir(tex_file) or not os.path.exists(tex_file):
        return []

    lines = get_lines_from_file(tex_file)

    # possible figure lead-ins
    figure_head = u'\\begin{figure'  # also matches figure*
    figure_wrap_head = u'\\begin{wrapfigure'
    figure_tail = u'\\end{figure'  # also matches figure*
    figure_wrap_tail = u'\\end{wrapfigure'
    picture_head = u'\\begin{picture}'
    displaymath_head = u'\\begin{displaymath}'
    subfloat_head = u'\\subfloat'
    subfig_head = u'\\subfigure'
    includegraphics_head = u'\\includegraphics'
    include_head = r'\\include(?!graphics)'  # matches only \include{}
    epsfig_head = u'\\epsfig'
    input_head = u'\\input'
    # possible caption lead-ins
    caption_head = u'\\caption'
    figcaption_head = u'\\figcaption'
    label_head = u'\\label'
    rotate = u'rotate='
    angle = u'angle='
    eps_tail = u'.eps'
    ps_tail = u'.ps'

    doc_head = u'\\begin{document}'
    doc_tail = u'\\end{document}'

    extracted_image_data = []
    cur_image = ''
    caption = ''
    labels = []
    active_label = ""

    # cut out shit before the doc head
    if primary:
        for line_index in range(len(lines)):
            if lines[line_index].find(doc_head) < 0:
                lines[line_index] = ''
            else:
                break

    # are we using commas in filenames here?
    commas_okay = False

    for dummy1, dummy2, filenames in \
            os.walk(os.path.split(os.path.split(tex_file)[0])[0]):
        for filename in filenames:
            if filename.find(',') > -1:
                commas_okay = True
                break

    # a comment is a % not preceded by a \
    comment = re.compile("(?<!\\\\)%")

    for line_index in range(len(lines)):
        # get rid of pesky comments by splitting where the comment is
        # and keeping only the part before the %
        line = comment.split(lines[line_index])[0]
        line = line.strip()
        lines[line_index] = line

    in_figure_tag = 0

    for line_index in range(len(lines)):
        line = lines[line_index]

        if line == '':
            continue
        if line.find(doc_tail) > -1:
            break

        r"""
        FIGURE -
        structure of a figure:
        \begin{figure}
        \formatting...
        \includegraphics[someoptions]{FILENAME}
        \caption{CAPTION}  %caption and includegraphics may be switched!
        \end{figure}
        """

        index = max([line.find(figure_head), line.find(figure_wrap_head)])
        if index > -1:
            in_figure_tag = 1
            # some punks don't like to put things in the figure tag.  so we
            # just want to see if there is anything that is sitting outside
            # of it when we find it
            cur_image, caption, extracted_image_data = put_it_together(
                cur_image, caption,
                active_label, extracted_image_data,
                line_index, lines)

        # here, you jerks, just make it so that it's fecking impossible to
        # figure out your damn inclusion types

        index = max([line.find(eps_tail), line.find(ps_tail),
                     line.find(epsfig_head)])
        if index > -1:
            if line.find(eps_tail) > -1 or line.find(ps_tail) > -1:
                ext = True
            else:
                ext = False
            filenames = intelligently_find_filenames(line, ext=ext,
                                                     commas_okay=commas_okay)

            # try to look ahead!  sometimes there are better matches after
            if line_index < len(lines) - 1:
                filenames.extend(intelligently_find_filenames(
                    lines[line_index + 1],
                    commas_okay=commas_okay))
            if line_index < len(lines) - 2:
                filenames.extend(intelligently_find_filenames(
                    lines[line_index + 2],
                    commas_okay=commas_okay))

            for filename in filenames:
                filename = filename.encode('utf-8', 'ignore')
                if cur_image == '':
                    cur_image = filename
                elif type(cur_image) == list:
                    if type(cur_image[SUB_CAPTION_OR_IMAGE]) == list:
                        cur_image[SUB_CAPTION_OR_IMAGE].append(filename)
                    else:
                        cur_image[SUB_CAPTION_OR_IMAGE] = [filename]
                else:
                    cur_image = ['', [cur_image, filename]]

        """
        Rotate and angle
        """
        index = max(line.find(rotate), line.find(angle))
        if index > -1:
            # which is the image associated to it?
            filenames = intelligently_find_filenames(line,
                                                     commas_okay=commas_okay)
            # try the line after and the line before
            if line_index + 1 < len(lines):
                filenames.extend(intelligently_find_filenames(
                    lines[line_index + 1],
                    commas_okay=commas_okay))
            if line_index > 1:
                filenames.extend(intelligently_find_filenames(
                    lines[line_index - 1],
                    commas_okay=commas_okay))
            already_tried = []
            for filename in filenames:
                if filename != 'ERROR' and filename not in already_tried:
                    if rotate_image(filename, line, sdir, image_list):
                        break
                    already_tried.append(filename)

        r"""
        INCLUDEGRAPHICS -
        structure of includegraphics:
        \includegraphics[someoptions]{FILENAME}
        """
        index = line.find(includegraphics_head)
        if index > -1:
            open_curly, open_curly_line, close_curly, dummy = \
                find_open_and_close_braces(line_index, index, '{', lines)
            filename = lines[open_curly_line][open_curly + 1:close_curly]
            if cur_image == '':
                cur_image = filename
            elif type(cur_image) == list:
                if type(cur_image[SUB_CAPTION_OR_IMAGE]) == list:
                    cur_image[SUB_CAPTION_OR_IMAGE].append(filename)
                else:
                    cur_image[SUB_CAPTION_OR_IMAGE] = [filename]
            else:
                cur_image = ['', [cur_image, filename]]

        r"""
        {\input{FILENAME}}
        \caption{CAPTION}

        This input is ambiguous, since input is also used for things like
        inclusion of data from other LaTeX files directly.
        """
        index = line.find(input_head)
        if index > -1:
            new_tex_names = intelligently_find_filenames(
                line, TeX=True,
                commas_okay=commas_okay)
            for new_tex_name in new_tex_names:
                if new_tex_name != 'ERROR':
                    new_tex_file = get_tex_location(new_tex_name, tex_file)
                    if new_tex_file and primary:  # to kill recursion
                        extracted_image_data.extend(extract_captions(
                            new_tex_file, sdir,
                            image_list,
                            primary=False
                        ))

        r"""
        INCLUDE -
        structure of include:
        \include{FILENAME}
        """
        index = re.match(include_head, line)
        if index:
            new_tex_names = intelligently_find_filenames(
                line, TeX=True,
                commas_okay=commas_okay)
            for new_tex_name in new_tex_names:
                if new_tex_name != 'ERROR':
                    new_tex_file = get_tex_location(new_tex_name, tex_file)
                    if new_tex_file and primary:  # to kill recursion
                        extracted_image_data.extend(extract_captions(
                            new_tex_file, sdir,
                            image_list,
                            primary=False
                        ))

        """PICTURE"""

        index = line.find(picture_head)
        if index > -1:
            # structure of a picture:
            # \begin{picture}
            # ....not worrying about this now
            # print('found picture tag')
            # FIXME
            pass

        """DISPLAYMATH"""

        index = line.find(displaymath_head)
        if index > -1:
            # structure of a displaymath:
            # \begin{displaymath}
            # ....not worrying about this now
            # print('found displaymath tag')
            # FIXME
            pass

        r"""
        CAPTIONS -
        structure of a caption:
        \caption[someoptions]{CAPTION}
        or
        \caption{CAPTION}
        or
        \caption{{options}{CAPTION}}
        """

        index = max([line.find(caption_head), line.find(figcaption_head)])
        if index > -1:
            open_curly, open_curly_line, close_curly, close_curly_line = \
                find_open_and_close_braces(line_index, index, '{', lines)

            cap_begin = open_curly + 1

            cur_caption = assemble_caption(
                open_curly_line, cap_begin,
                close_curly_line, close_curly, lines)

            if caption == '':
                caption = cur_caption
            elif type(caption) == list:
                if type(caption[SUB_CAPTION_OR_IMAGE]) == list:
                    caption[SUB_CAPTION_OR_IMAGE].append(cur_caption)
                else:
                    caption[SUB_CAPTION_OR_IMAGE] = [cur_caption]
            elif caption != cur_caption:
                caption = ['', [caption, cur_caption]]

        r"""
        SUBFIGURES -
        structure of a subfigure (inside a figure tag):
        \subfigure[CAPTION]{
        \includegraphics[options]{FILENAME}}

        or

        SUBFLOATS -
        structure of a subfloat (inside of a figure tag):
        \subfloat[CAPTION]{
        \includegraphics[options]{FILENAME}}


        also associated with the overall caption of the enclosing figure
        """

        index = max([line.find(subfloat_head), line.find(subfig_head)])
        if index > -1:
            # we need a different structure for keeping track of several
            # captions and images
            if type(cur_image) != list:
                cur_image = [cur_image, []]
            if type(caption) != list:
                caption = [caption, []]

            open_square, open_square_line, close_square, close_square_line = \
                find_open_and_close_braces(line_index, index, '[', lines)
            cap_begin = open_square + 1

            sub_caption = assemble_caption(open_square_line,
                                           cap_begin, close_square_line,
                                           close_square, lines)
            caption[SUB_CAPTION_OR_IMAGE].append(sub_caption)

            index_cpy = index

            # find the graphics tag to get the filename
            # it is okay if we eat lines here
            index = line.find(includegraphics_head)
            while index == -1 and (line_index + 1) < len(lines):
                line_index += 1
                line = lines[line_index]
                index = line.find(includegraphics_head)
            if line_index == len(lines):
                # didn't find the image name on line
                line_index = index_cpy

            open_curly, open_curly_line, close_curly, dummy = \
                find_open_and_close_braces(line_index,
                                           index, '{', lines)
            sub_image = lines[open_curly_line][open_curly + 1:close_curly]

            cur_image[SUB_CAPTION_OR_IMAGE].append(sub_image)

        r"""
        LABELS -
        structure of a label:
        \label{somelabelnamewhichprobablyincludesacolon}

        Labels are used to tag images and will later be used in ref tags
        to reference them.  This is interesting because in effect the refs
        to a plot are additional caption for it.

        Notes: labels can be used for many more things than just plots.
        We'll have to experiment with how to best associate a label with an
        image.. if it's in the caption, it's easy.  If it's in a figure, it's
        still okay... but the images that aren't in figure tags are numerous.
        """
        index = line.find(label_head)
        if index > -1 and in_figure_tag:
            open_curly, open_curly_line, close_curly, dummy =\
                find_open_and_close_braces(line_index,
                                           index, '{', lines)
            label = lines[open_curly_line][open_curly + 1:close_curly]
            if label not in labels:
                active_label = label
            labels.append(label)

        """
        FIGURE

        important: we put the check for the end of the figure at the end
        of the loop in case some pathological person puts everything in one
        line
        """
        index = max([
            line.find(figure_tail),
            line.find(figure_wrap_tail),
            line.find(doc_tail)
        ])
        if index > -1:
            in_figure_tag = 0
            cur_image, caption, extracted_image_data = \
                put_it_together(cur_image, caption, active_label,
                                extracted_image_data,
                                line_index, lines)
        """
        END DOCUMENT

        we shouldn't look at anything after the end document tag is found
        """

        index = line.find(doc_tail)
        if index > -1:
            break

    return extracted_image_data


def put_it_together(cur_image, caption, context, extracted_image_data,
                    line_index, lines):
    """Put it together.

    Takes the current image(s) and caption(s) and assembles them into
    something useful in the extracted_image_data list.

    :param: cur_image (string || list): the image currently being dealt with,
        or the list of images, in the case of subimages
    :param: caption (string || list): the caption or captions currently in
        scope
    :param: extracted_image_data ([(string, string), (string, string), ...]):
        a list of tuples of images matched to captions from this document.
    :param: line_index (int): the index where we are in the lines (for
        searchback and searchforward purposes)
    :param: lines ([string, string, ...]): the lines in the TeX

    :return: (cur_image, caption, extracted_image_data): the same arguments it
        was sent, processed appropriately
    """
    if type(cur_image) == list:
        if cur_image[MAIN_CAPTION_OR_IMAGE] == 'ERROR':
            cur_image[MAIN_CAPTION_OR_IMAGE] = ''
        for image in cur_image[SUB_CAPTION_OR_IMAGE]:
            if image == 'ERROR':
                cur_image[SUB_CAPTION_OR_IMAGE].remove(image)

    if cur_image != '' and caption != '':

        if type(cur_image) == list and type(caption) == list:

            if cur_image[MAIN_CAPTION_OR_IMAGE] != '' and\
                    caption[MAIN_CAPTION_OR_IMAGE] != '':
                extracted_image_data.append(
                    (cur_image[MAIN_CAPTION_OR_IMAGE],
                     caption[MAIN_CAPTION_OR_IMAGE],
                     context))
            if type(cur_image[MAIN_CAPTION_OR_IMAGE]) == list:
                # why is the main image a list?
                # it's a good idea to attach the main caption to other
                # things, but the main image can only be used once
                cur_image[MAIN_CAPTION_OR_IMAGE] = ''

            if type(cur_image[SUB_CAPTION_OR_IMAGE]) == list:
                if type(caption[SUB_CAPTION_OR_IMAGE]) == list:
                    for index in \
                            range(len(cur_image[SUB_CAPTION_OR_IMAGE])):
                        if index < len(caption[SUB_CAPTION_OR_IMAGE]):
                            long_caption = \
                                caption[MAIN_CAPTION_OR_IMAGE] + ' : ' + \
                                caption[SUB_CAPTION_OR_IMAGE][index]
                        else:
                            long_caption = \
                                caption[MAIN_CAPTION_OR_IMAGE] + ' : ' + \
                                'Caption not extracted'
                        extracted_image_data.append(
                            (cur_image[SUB_CAPTION_OR_IMAGE][index],
                             long_caption, context))

                else:
                    long_caption = caption[MAIN_CAPTION_OR_IMAGE] + \
                        ' : ' + caption[SUB_CAPTION_OR_IMAGE]
                    for sub_image in cur_image[SUB_CAPTION_OR_IMAGE]:
                        extracted_image_data.append(
                            (sub_image, long_caption, context))

            else:
                if type(caption[SUB_CAPTION_OR_IMAGE]) == list:
                    long_caption = caption[MAIN_CAPTION_OR_IMAGE]
                    for sub_cap in caption[SUB_CAPTION_OR_IMAGE]:
                        long_caption = long_caption + ' : ' + sub_cap
                    extracted_image_data.append(
                        (cur_image[SUB_CAPTION_OR_IMAGE], long_caption,
                         context))
                else:
                    # wtf are they lists for?
                    extracted_image_data.append(
                        (cur_image[SUB_CAPTION_OR_IMAGE],
                         caption[SUB_CAPTION_OR_IMAGE], context))

        elif type(cur_image) == list:
            if cur_image[MAIN_CAPTION_OR_IMAGE] != '':
                extracted_image_data.append(
                    (cur_image[MAIN_CAPTION_OR_IMAGE], caption, context))
            if type(cur_image[SUB_CAPTION_OR_IMAGE]) == list:
                for image in cur_image[SUB_CAPTION_OR_IMAGE]:
                    extracted_image_data.append((image, caption, context))
            else:
                extracted_image_data.append(
                    (cur_image[SUB_CAPTION_OR_IMAGE], caption, context))

        elif type(caption) == list:
            if caption[MAIN_CAPTION_OR_IMAGE] != '':
                extracted_image_data.append(
                    (cur_image, caption[MAIN_CAPTION_OR_IMAGE], context))
            if type(caption[SUB_CAPTION_OR_IMAGE]) == list:
                # multiple caps for one image:
                long_caption = caption[MAIN_CAPTION_OR_IMAGE]
                for subcap in caption[SUB_CAPTION_OR_IMAGE]:
                    if long_caption != '':
                        long_caption += ' : '
                    long_caption += subcap
                extracted_image_data.append((cur_image, long_caption, context))
            else:
                extracted_image_data.append(
                    (cur_image, caption[SUB_CAPTION_OR_IMAGE]. context))

        else:
            extracted_image_data.append((cur_image, caption, context))

    elif cur_image != '' and caption == '':
        # we may have missed the caption somewhere.
        REASONABLE_SEARCHBACK = 25
        REASONABLE_SEARCHFORWARD = 5
        curly_no_tag_preceding = '(?<!\\w){'

        for searchback in range(REASONABLE_SEARCHBACK):
            if line_index - searchback < 0:
                continue

            back_line = lines[line_index - searchback]
            m = re.search(curly_no_tag_preceding, back_line)
            if m:
                open_curly = m.start()
                open_curly, open_curly_line, close_curly, \
                    close_curly_line = find_open_and_close_braces(
                        line_index - searchback, open_curly, '{', lines)

                cap_begin = open_curly + 1

                caption = assemble_caption(open_curly_line, cap_begin,
                                           close_curly_line, close_curly,
                                           lines)

                if type(cur_image) == list:
                    extracted_image_data.append(
                        (cur_image[MAIN_CAPTION_OR_IMAGE], caption, context))
                    for sub_img in cur_image[SUB_CAPTION_OR_IMAGE]:
                        extracted_image_data.append(
                            (sub_img, caption, context))
                else:
                    extracted_image_data.append((cur_image, caption, context))
                    break

        if caption == '':
            for searchforward in range(REASONABLE_SEARCHFORWARD):
                if line_index + searchforward >= len(lines):
                    break

                fwd_line = lines[line_index + searchforward]
                m = re.search(curly_no_tag_preceding, fwd_line)

                if m:
                    open_curly = m.start()
                    open_curly, open_curly_line, close_curly,\
                        close_curly_line = find_open_and_close_braces(
                            line_index + searchforward, open_curly, '{', lines)

                    cap_begin = open_curly + 1

                    caption = assemble_caption(open_curly_line,
                                               cap_begin, close_curly_line,
                                               close_curly, lines)

                    if type(cur_image) == list:
                        extracted_image_data.append(
                            (cur_image[MAIN_CAPTION_OR_IMAGE],
                             caption, context))
                        for sub_img in cur_image[SUB_CAPTION_OR_IMAGE]:
                            extracted_image_data.append(
                                (sub_img, caption, context))
                    else:
                        extracted_image_data.append(
                            (cur_image, caption, context))
                    break

        if caption == '':
            if type(cur_image) == list:
                extracted_image_data.append(
                    (cur_image[MAIN_CAPTION_OR_IMAGE], 'No caption found',
                     context))
                for sub_img in cur_image[SUB_CAPTION_OR_IMAGE]:
                    extracted_image_data.append(
                        (sub_img, 'No caption', context))
            else:
                extracted_image_data.append(
                    (cur_image, 'No caption found', context))

    elif caption != '' and cur_image == '':
        if type(caption) == list:
            long_caption = caption[MAIN_CAPTION_OR_IMAGE]
            for subcap in caption[SUB_CAPTION_OR_IMAGE]:
                long_caption = long_caption + ': ' + subcap
        else:
            long_caption = caption
        extracted_image_data.append(('', 'noimg' + long_caption, context))

    # if we're leaving the figure, no sense keeping the data
    cur_image = ''
    caption = ''

    return cur_image, caption, extracted_image_data


def intelligently_find_filenames(line, TeX=False, ext=False,
                                 commas_okay=False):
    """Intelligently find filenames.

    Find the filename in the line.  We don't support all filenames!  Just eps
    and ps for now.

    :param: line (string): the line we want to get a filename out of

    :return: filename ([string, ...]): what is probably the name of the file(s)
    """
    files_included = ['ERROR']

    if commas_okay:
        valid_for_filename = '\\s*[A-Za-z0-9\\-\\=\\+/\\\\_\\.,%#]+'
    else:
        valid_for_filename = '\\s*[A-Za-z0-9\\-\\=\\+/\\\\_\\.%#]+'

    if ext:
        valid_for_filename += r'\.e*ps[texfi2]*'

    if TeX:
        valid_for_filename += r'[\.latex]*'

    file_inclusion = re.findall('=' + valid_for_filename + '[ ,]', line)

    if len(file_inclusion) > 0:
        # right now it looks like '=FILENAME,' or '=FILENAME '
        for file_included in file_inclusion:
            files_included.append(file_included[1:-1])

    file_inclusion = re.findall('(?:[ps]*file=|figure=)' +
                                valid_for_filename + '[,\\]} ]*', line)

    if len(file_inclusion) > 0:
        # still has the =
        for file_included in file_inclusion:
            part_before_equals = file_included.split('=')[0]
            if len(part_before_equals) != file_included:
                file_included = file_included[
                    len(part_before_equals) + 1:].strip()
            if file_included not in files_included:
                files_included.append(file_included)

    file_inclusion = re.findall(
        '["\'{\\[]' + valid_for_filename + '[}\\],"\']',
        line)

    if len(file_inclusion) > 0:
        # right now it's got the {} or [] or "" or '' around it still
        for file_included in file_inclusion:
            file_included = file_included[1:-1]
            file_included = file_included.strip()
            if file_included not in files_included:
                files_included.append(file_included)

    file_inclusion = re.findall('^' + valid_for_filename + '$', line)

    if len(file_inclusion) > 0:
        for file_included in file_inclusion:
            file_included = file_included.strip()
            if file_included not in files_included:
                files_included.append(file_included)

    file_inclusion = re.findall('^' + valid_for_filename + '[,\\} $]', line)

    if len(file_inclusion) > 0:
        for file_included in file_inclusion:
            file_included = file_included.strip()
            if file_included not in files_included:
                files_included.append(file_included)

    file_inclusion = re.findall('\\s*' + valid_for_filename + '\\s*$', line)

    if len(file_inclusion) > 0:
        for file_included in file_inclusion:
            file_included = file_included.strip()
            if file_included not in files_included:
                files_included.append(file_included)

    if files_included != ['ERROR']:
        files_included = files_included[1:]  # cut off the dummy

    for file_included in files_included:
        if file_included == '':
            files_included.remove(file_included)
        if ' ' in file_included:
            for subfile in file_included.split(' '):
                if subfile not in files_included:
                    files_included.append(subfile)
        if ',' in file_included:
            for subfile in file_included.split(' '):
                if subfile not in files_included:
                    files_included.append(subfile)

    return files_included


def get_lines_from_file(filepath, encoding="UTF-8"):
    """Return an iterator over lines."""
    try:
        fd = codecs.open(filepath, 'r', encoding)
        lines = fd.readlines()
    except UnicodeDecodeError:
        # Fall back to 'ISO-8859-1'
        fd = codecs.open(filepath, 'r', 'ISO-8859-1')
        lines = fd.readlines()
    finally:
        fd.close()
    return lines
