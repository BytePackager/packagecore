##
# @file buildvariables_test.py
# @brief Unit tests for the buildvariables object.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-03


import unittest
from .buildvariables import \
    BuildVariables, \
    DESTDIR_KEY, \
    SOURCEDIR_KEY


TEST_DESTDIR = "/tmp/fakeroot"
TEST_SOURCEDIR = "/tmp/my-pkg/src"


class MockFile:
    def __init__(self):
        self._buffer = []

    def write(self, chunk):
        self._buffer.append(chunk)

    def getBuffer(self):
        return ''.join(self._buffer)


class TestBuildVariables(unittest.TestCase):
    def test_write(self):
        buildVars = BuildVariables(
            destDir=TEST_DESTDIR, sourceDir=TEST_SOURCEDIR)

        mockFile = MockFile()
        buildVars.write(mockFile)

        output = mockFile.getBuffer()
        self.assertTrue(("%s=\"%s\"\n" %
                         (DESTDIR_KEY, TEST_DESTDIR)) in output)
        self.assertTrue(
            ("%s=\"%s\"\n" % (SOURCEDIR_KEY, TEST_SOURCEDIR)) in output)

    def test_generate(self):
        buildVars = BuildVariables(
            destDir=TEST_DESTDIR, sourceDir=TEST_SOURCEDIR)

        data = buildVars.generate()

        self.assertEqual(data[DESTDIR_KEY], TEST_DESTDIR)
        self.assertEqual(data[SOURCEDIR_KEY], TEST_SOURCEDIR)
