..
    This file is part of plotextractor.
    Copyright (C) 2015, 2016, 2018 CERN.

    plotextractor is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    plotextractor is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with plotextractor; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Changes
=======

Version 0.2.2 (2019-10-24)

- Try to preserve the ordering of figures.

Version 0.2.1 (2018-09-07)

- Handle utf-8 in paths inside the tarball.

Version 0.2.0 (2018-02-07)

- Ignore hidden/metadata files in the tarball.
- Handle relative paths in the tarball.

Version 0.1.6 (2016-12-01)

- Sets the mtime for all members of the tarball to current time before
  unpacking.

Version 0.1.5 (2016-05-25)

- Properly raises an exception when no TeX files are found in an archive.
- More fixes to image path extraction and more robust image handling.

Version 0.1.4 (2016-03-22)

- Fixes linking images from TeX reference when images are referred
  to without specifying full relative folder path.

Version 0.1.3 (2016-03-17)

- Properly supports cases where images are located in
  a nested folder inside the extracted tarballs root folder.

Version 0.1.2 (2015-12-08)

- Adds wrapfigure support.
- Catches problems with image conversions.
- More robust handling of image rotations in TeX sources.
- Removes unicode_literals usage.

Version 0.1.1 (2015-12-04)

- Improves extraction from TeX file by reading files with encoding.

Version 0.1.0 (2015-10-19)

- Initial export from Invenio Software <https://github.com/inveniosoftware/invenio>
- Restructured into stripped down, standalone version
