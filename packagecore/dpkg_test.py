##
# @file chroot_test.py
# @brief Unit tests for the DebianPackage class.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-27


import unittest
import os

from .builddata import generateMockData
from .docker import MockContainer
from .dpkg import DebianPackage


class TestDpkg(unittest.TestCase):
    def test_generateControlFile(self):
        data = generateMockData()
        container = MockContainer()
        build = DebianPackage(data)

        build.prep(container)

        with open(os.path.join(container.getSharedDir(), "%s-%s/DEBIAN/control" %
                               (data.name, data.version)), "r") as ctrlFile:
            content = ctrlFile.read()

        # perform a simplified check on the control file
        self.assertGreaterEqual(content.find("Package: %s" % data.name), 0)

    def test_generateCopyrightFile(self):
        data = generateMockData()
        container = MockContainer()
        build = DebianPackage(data)

        build.prep(container)

        with open(os.path.join(container.getSharedDir(), "%s-%s/DEBIAN/copyright" %
                               (data.name, data.version)), "r") as ctrlFile:
            content = ctrlFile.read()

        # perform a simplified check on the control file
        self.assertGreaterEqual(content.find("License: %s" % data.license), 0)

    def test_postInstallFile(self):
        data = generateMockData()
        container = MockContainer()
        build = DebianPackage(data)

        build.prep(container)

        with open(os.path.join(container.getSharedDir(), "%s-%s/DEBIAN/postinst" %
                               (data.name, data.version)), "r") as ctrlFile:
            content = ctrlFile.read()

        # perform a simplified check on the control file
        self.assertEqual(content.find("#!/bin/bash"), 0)
        self.assertGreaterEqual(content.find("adduser"), 0)

    def test_getName(self):
        data = generateMockData()
        build = DebianPackage(data)

        name = build.getName()

        self.assertGreaterEqual(name.find(data.name), 0)
        self.assertGreaterEqual(name.find(data.version), 0)
