# -*- coding: utf-8 -*-
#
# This file is part of plotextractor.
# Copyright (C) 2015, 2016, 2020 CERN.
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

import pytest
import magic
import io
import os
import pkg_resources
import tarfile
from shutil import rmtree
from tempfile import mkdtemp

from plotextractor.converter import detect_images_and_tex, untar, convert_images


def write_tarball(path, members):
    """Build a tarball from (name, type[, link target]) tuples."""
    with tarfile.open(str(path), "w") as tarball:
        for entry in members:
            name, member_type = entry[0], entry[1]
            member = tarfile.TarInfo(name)
            member.type = member_type
            member.mode = 0o755 if member_type == tarfile.DIRTYPE else 0o644
            if member_type == tarfile.REGTYPE:
                content = b"content"
                member.size = len(content)
                tarball.addfile(member, io.BytesIO(content))
            else:
                member.linkname = entry[2] if len(entry) > 2 else "../outside.txt"
                tarball.addfile(member)


def test_untar_skips_members_that_escape_the_destination(tmpdir):
    archive = tmpdir.join("traversal.tar")
    destination = tmpdir.mkdir("destination")
    write_tarball(
        archive,
        [
            ("safe.txt", tarfile.REGTYPE),
            ("../outside.txt", tarfile.REGTYPE),
            ("../../outside.txt", tarfile.REGTYPE),
            ("/outside.txt", tarfile.REGTYPE),
        ],
    )

    extracted = untar(str(archive), str(destination))

    assert extracted == [str(destination.join("safe.txt"))]
    assert sorted(os.listdir(str(destination))) == ["safe.txt"]
    assert not tmpdir.join("outside.txt").exists()


def test_untar_skips_links_and_device_nodes(tmpdir):
    archive = tmpdir.join("link.tar")
    destination = tmpdir.mkdir("destination")
    write_tarball(
        archive,
        [
            ("paper.tex", tarfile.REGTYPE),
            ("relative", tarfile.SYMTYPE, "../outside.txt"),
            ("absolute", tarfile.SYMTYPE, "/etc/passwd"),
            ("hard", tarfile.LNKTYPE, "../outside.txt"),
            ("chardev", tarfile.CHRTYPE),
            ("blockdev", tarfile.BLKTYPE),
            ("fifo", tarfile.FIFOTYPE),
        ],
    )

    extracted = untar(str(archive), str(destination))

    assert extracted == [str(destination.join("paper.tex"))]
    assert sorted(os.listdir(str(destination))) == ["paper.tex"]


def test_untar_keeps_links_that_stay_inside_the_destination(tmpdir):
    """An archive may legitimately carry the same figure twice."""
    archive = tmpdir.join("paper.tar")
    destination = tmpdir.mkdir("destination")
    write_tarball(
        archive,
        [
            ("figs", tarfile.DIRTYPE),
            ("figs/a.png", tarfile.REGTYPE),
            ("figs/a_hard.png", tarfile.LNKTYPE, "figs/a.png"),
            ("figs/a_soft.png", tarfile.SYMTYPE, "a.png"),
        ],
    )

    extracted = untar(str(archive), str(destination))

    names = ["figs", "figs/a.png", "figs/a_hard.png", "figs/a_soft.png"]
    assert extracted == [str(destination.join(name)) for name in names]
    original = str(destination.join("figs", "a.png"))
    assert (
        os.stat(str(destination.join("figs", "a_hard.png"))).st_ino
        == os.stat(original).st_ino
    )
    assert os.path.realpath(str(destination.join("figs", "a_soft.png"))) == original


def test_untar_skips_paths_through_an_existing_symlink(tmpdir):
    archive = tmpdir.join("symlink-path.tar")
    destination = tmpdir.mkdir("destination")
    outside = tmpdir.mkdir("outside")
    os.symlink(str(outside), str(destination.join("linked")))
    write_tarball(
        archive,
        [("paper.tex", tarfile.REGTYPE), ("linked/file.txt", tarfile.REGTYPE)],
    )

    extracted = untar(str(archive), str(destination))

    assert extracted == [str(destination.join("paper.tex"))]
    assert not outside.join("file.txt").exists()


def test_detect_images_and_tex_ignores_hidden_metadata_files():
    tarball_filename = pkg_resources.resource_filename(
        __name__, os.path.join("data", "1704.02281.tar.gz")
    )
    try:
        temporary_dir = mkdtemp()
        file_list = untar(tarball_filename, temporary_dir)
        image_files, _ = detect_images_and_tex(file_list)
        # Ensure image_list doesn't contain a hidden or metadata file
        for f in image_files:
            assert (
                "image" in magic.from_file(f).lower()
                or "eps" in magic.from_file(f).lower()
                or "Postscript" in magic.from_file(f)
            )
    finally:
        rmtree(temporary_dir)


@pytest.mark.xfail(
    reason="By reducing the dpi to 100, we are able to extract the image"
)
def test_skip_decompression_bomb_error():
    pdf = pkg_resources.resource_filename(
        __name__, os.path.join("data", "eada5d4d-efb3-4e89-9049-84c3e0849922.pdf")
    )
    assert len(convert_images([pdf])) == 0


def test_conversion_pdf():
    pdf = pkg_resources.resource_filename(
        __name__, os.path.join("data", "eada5d4d-efb3-4e89-9049-84c3e0849922.pdf")
    )
    assert len(convert_images([pdf])) == 1


def test_conversion_eps():
    eps = pkg_resources.resource_filename(__name__, os.path.join("data", "circle.eps"))
    assert len(convert_images([eps])) == 1


def test_compress_big_png():
    png = pkg_resources.resource_filename(
        __name__, os.path.join("data", "big_image.png")
    )

    assert len(convert_images([png])) == 1


def test_compress_big_jpg():
    jpg = pkg_resources.resource_filename(
        __name__, os.path.join("data", "random_image.jpg")
    )

    assert len(convert_images([jpg])) == 1


def test_compress_skips_corrupted_png():
    corrupted = pkg_resources.resource_filename(
        __name__, os.path.join("data", "corrupted_large.png")
    )

    assert len(convert_images([corrupted])) == 0


def test_compress_high_segment_jpg():
    jpg = pkg_resources.resource_filename(
        __name__, os.path.join("data", "Pipeline_2.jpeg")
    )

    assert len(convert_images([jpg])) == 1
