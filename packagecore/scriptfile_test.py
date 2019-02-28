##
# @file scriptfile_test.py
# @brief Unit tests for ScriptFile class.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-21


import unittest
import subprocess
import os

from .scriptfile import generateScript


class TestScriptFile(unittest.TestCase):
    def test_generateScriptEnv(self):
        filename = "/tmp/test.sh"

        testFile = "/tmp/test.txt"

        cmds = """
X="${ENV_TEST}"

touch "${X}"

exit 0
"""

        generateScript(filename, cmds, {"ENV_TEST": testFile})

        # check permissions
        self.assertTrue(os.access(filename, os.F_OK))
        self.assertTrue(os.access(filename, os.X_OK | os.R_OK))

        # execute the script and expect it to create the file
        status = subprocess.call([filename])
        self.assertEqual(status, 0)

        # check that the testFile got created by the script
        self.assertTrue(os.access(testFile, os.F_OK))

        # cleanup
        os.remove(filename)
        os.remove(testFile)
