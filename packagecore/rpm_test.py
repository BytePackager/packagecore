##
# @file rpm_test.py
# @brief Unit tests for the RPM class.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-28


import unittest

from .builddata import generateMockData
from .docker import MockContainer
from .rpm import RPM
from .rpm import RPM_DNF


class TestRPM(unittest.TestCase):
    def test_generateSpecFile(self):
        data = generateMockData()
        container = MockContainer()
        binary = RPM(data, RPM_DNF)

        binary.prep(container)

        with open(binary.getSpecFileName(), "r") as ctrlFile:
            content = ctrlFile.read()

        # perform a simplified check on the control file
        self.assertGreaterEqual(content.find("Name: %s" % data.name), 0)

    def test_getName(self):
        data = generateMockData()
        binary = RPM(data, RPM_DNF)

        name = binary.getName()

        self.assertGreaterEqual(name.find(data.name), 0)
        self.assertGreaterEqual(name.find(data.version), 0)


if __name__ == '__main__':
    unittest.main()
