##
# @file docker_test.py
# @brief Unit tests for docker.py
# @author Dominique LaSalle <dominique@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-08-08


import unittest

from .docker import \
    Docker, \
    DockerError
from .distributions import DATA


class TestDocker(unittest.TestCase):
    def test_runCommand(self):
        # attempt to download and run a simple ls on a container
        docker = Docker()

        # centos is nice and stable
        container = docker.start(DATA["centos7.3"]["dockerImage"])

        # should succeed
        container.execute("ls")

        # should fail
        try:
            cmd = ["ls", "/dev/null/nothing"]
            container.execute(cmd)

            # should have failed
            self.fail("'%s' did not throw an exception." % str(cmd))
        except DockerError:
            # success
            pass

        docker.stop(container)
