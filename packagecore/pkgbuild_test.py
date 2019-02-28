##
# @file pkgbuild_test.py
# @brief Unit tests for the pkgbuild class.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-28


import unittest
import os

from .builddata import generateMockData
from .docker import MockContainer
from .pkgbuild import PkgBuild


class TestPkgBuild(unittest.TestCase):
    def test_generatePKGBUILDFile(self):
        data = generateMockData()
        container = MockContainer()
        build = PkgBuild(data)

        build.prep(container)

        with open(os.path.join(container.getSharedDir(), "arch-pkg/PKGBUILD")) as ctrlFile:
            content = ctrlFile.read()

        # perform a simplified check on the control file
        self.assertGreaterEqual(content.find("pkgname=%s" % data.name), 0)

    def test_getName(self):
        data = generateMockData()
        build = PkgBuild(data)

        name = build.getName()

        self.assertGreaterEqual(name.find(data.name), 0)
        self.assertGreaterEqual(name.find(data.version), 0)
