##
# @file packager_test.py
# @brief Unit tests for the Packager class.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-16


import unittest


from .configparser import parse


CONF = {
    "name": "packagecore",
    "maintainer": "packagecore@solidlake.com",
    "license": "GPL2",
    "summary": "Utility for generating Linux packages.",
    "homepage": "https://github.com/bytepackager/packagecore",
    "commands": {
        "precompile": "echo \"Nothing to do\"",
        "compile": "echo \"Nothing to compile.\"",
        "install": "python3 setup.py install --prefix=/usr --root=\"${BP_DESTDIR}\"",
        "postinstall": "echo \"Finished installing.\"",
        "testinstall": "packagecore -h || exit 1"
    },
    "packages": {
        "archlinux": {
            "builddeps": [
                "python",
                "python-setuptools"
            ],
            "deps": [
                "python",
                "python-yaml",
                "docker"
            ]
        },
        "fedora25": {
            "builddeps": [
                "python3",
                "python3-setuptools"
            ],
            "deps": [
                "python3",
                "python3-PyYAML",
                "docker"
            ],
        },
        "ubuntu17.10": {
            "builddeps": [
                "python3",
                "python3-setuptools"
            ],
            "deps": [
                "python3",
                "python3-yaml",
                "docker"
            ]
        }
    }
}


class TestPackager(unittest.TestCase):
    def test_init(self):
        builds = parse(CONF, "1.2.3", 4)

        for build in builds.values():
            self.assertEqual(build.name, CONF["name"])
            self.assertEqual(build.maintainer, CONF["maintainer"])
            self.assertEqual(build.license, CONF["license"])
            self.assertEqual(build.summary, CONF["summary"])
            self.assertEqual(build.homepage, CONF["homepage"])

            self.assertEqual(build.preCompileCommands,
                             CONF["commands"]["precompile"])
            self.assertEqual(build.installCommands,
                             CONF["commands"]["install"])
            self.assertEqual(build.postInstallCommands,
                             CONF["commands"]["postinstall"])
            self.assertEqual(build.testInstallCommands,
                             CONF["commands"]["testinstall"])

            # still need to test listed dependencies and overridden commands
