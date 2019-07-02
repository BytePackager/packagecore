##
# @file docker.py
# @brief Wrapper for utilizing docker containers.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-03


import os
import shutil
import sys
import random
import time
from subprocess import Popen, PIPE

from .scriptfile import generateScript

USERNAME = "builder"


def _makeDir(path):
    try:
        os.makedirs(path, 0o700)
    except FileExistsError:
        pass


class InputError(Exception):
    pass


class DockerError(Exception):
    pass


def _lxcAttachCommand(cmd, containerName):
    proc = Popen(["CID=\"$(docker inspect --format \"{{.Id}}\" %s)\" && "
                  "sudo lxc-attach -n \"${CID}\" "
                  "-f \"/var/lib/docker/containers/${CID}/config.lxc\" -- %s" %
                  (containerName, " ".join("\"{0}\"".format(c) for c in cmd))], shell=True)
    status = proc.wait()
    if status != 0:
        raise DockerError("Command '%s' returned %d." % (cmd, status))


def _dockerExecCommand(cmd, containerName):
    _checkedDockerCommand(["exec", containerName] + cmd)


def _checkedDockerCommand(cmd):
    print("RUN: %s" % " ".join(cmd))
    status = _uncheckedDockerCommand(cmd)
    if status != 0:
        raise DockerError("Command '%s' returned %d." % (cmd, status))


def _uncheckedDockerCommand(cmd):
    proc = Popen(["docker"] + cmd)
    status = proc.wait()
    return status


class MockContainer:
    def __init__(self):
        _makeDir(self.getSharedDir())

    def execute(self, cmd, cwd=None):
        pass

    def getSharedDir(self):
        return "/tmp/mock-dir"

    def copySource(self):
        pass

    def getSourceDir(self):
        return os.path.join(self.getSharedDir(), "src")

    def getImageName(self):
        return "linux:2.6"

    def stop(self):
        pass


class DockerContainer:
    ##
    # @brief Create a new docker container (left running).
    #
    # @param imageName The image to create it from.
    # @param useLXC Use lxc-attach instead of 'exec' command.
    # @param environment Map of environment variables to set inside of the
    # docker container.
    #
    # @return The docker container.
    def __init__(self, imageName, useLXC, environment=None):
        envCommands = []
        if environment:
            for name, value in environment.items():
                envCommands.append("-e")
                envCommands.append("%s=%s" % (name, value))

        self._image = imageName
        # get a unique name
        self._name = "packagecore-%x" % random.randrange(0, 2**64)

        self._useLXC = useLXC

        # make the shared directory
        if os.path.exists(self.getSharedDir()):
            shutil.rmtree(self.getSharedDir())
        _makeDir(self.getSharedDir())

        print("Starting docker container '%s'." % self._name)

        # hack to keep the container running
        self._proc = Popen(["docker", "run", "--name", self._name, "-v",
                            "%s:%s" % (self.getSharedDir(),
                                       self.getSharedDir())
                            ] + envCommands + [self._image, "tail", "-f", "/dev/null"],
                           stdout=PIPE, stderr=PIPE)

        # wait for our container to start
        running = False
        waitCycles = 0
        while self._proc.poll() is None:
            time.sleep(1)
            proc = Popen(["docker ps | grep '%s'" % self._name], shell=True)
            status = proc.wait()
            if status == 0:
                running = True
                break
            waitCycles += 1
            if waitCycles > 10:
                self._proc.kill()
                break
        if not running:
            stdout, stderr = self._proc.communicate()
            # flush stdout and stderr
            print(stdout)
            print(stderr)
            # try to cleanup a bit before we exit
            self.stop()
            raise DockerError("Container failed to start: %s" % self._name)

    ##
    # @brief Execute a command in the container.
    #
    # @param cmd The command to execute.
    #
    # @return None
    def execute(self, cmd):
        if isinstance(cmd, str):
            cmd = [cmd]
        if not isinstance(cmd, list):
            raise InputError("Requires list of commands, not '%s'" % type(cmd))
        if not self._useLXC:
            _checkedDockerCommand(["exec"] + [self._name] + cmd)
        else:
            _lxcAttachCommand(cmd, self._name)

    ##
    # @brief Generate and execute a script (i.e., write the contents of 'script'
    # to a file and execute it in bash.
    #
    # @param script The contents of the script to execute.
    #
    # @return None
    def executeScript(self, script, env=None):
        if not env:
            env = {}
        scriptName = os.path.join(self.getSharedDir(), ".packagecore_script")
        generateScript(scriptName, script, env)
        self.execute(scriptName)
        os.remove(scriptName)

    ##
    # @brief Get the directory shared between the host and the container.
    #
    # @return The shared directory (inside and outside of the container).
    def getSharedDir(self):
        return os.path.join("/tmp", self._name)

    ##
    # @brief Copy a directory of source code to inside of the container.
    #
    # @param localPath Where the source directory currently resides.
    #
    # @return None
    def copySource(self, localPath):
        shutil.copytree(localPath, self.getSourceDir())

    ##
    # @brief Get the source directory path inside of the container.
    #
    # @return
    def getSourceDir(self):
        return os.path.join(self.getSharedDir(), "src")

    ##
    # @brief Get the name of the underlying docker image.
    #
    # @return
    def getImageName(self):
        return self._image

    ##
    # @brief Get the running container's name.
    #
    # @return The name.
    def getName(self):
        return self._name

    def stop(self):
        print("Cleaning up self %s." % self.getName())
        # kill the running self
        _uncheckedDockerCommand(["kill", self.getName()])

        # remove self
        _uncheckedDockerCommand(["rm", self.getName()])

        # remove image -- later may be a preference to keep it
        #_uncheckedDockerCommand(["rmi", self.getImageName()])

        # remove shared directory
        try:
            if "BP_LEAVE_FILES" in os.environ:
                pass
            else:
                shutil.rmtree(self.getSharedDir())
        except OSError:
            print("Warning: failed to remove shared directory.", file=sys.stderr)


class Docker:
    ##
    # @brief Initialize a new docker wrapper.
    #
    # @return The new Docker wrapper.
    def __init__(self):
        # determine if we're using lxc or libcontainer
        grep = Popen(["docker", "info"], stdout=PIPE, stderr=PIPE)
        stdout = grep.communicate()[0]
        output = stdout.decode('utf8')
        print("DOCKER_INFO")
        print(output)
        if output.find("lxc-") < 0:
            print("Using 'exec'")
            self._useLXC = False
        else:
            print("Using 'lxc-attach'")
            self._useLXC = True

    ##
    # @brief Download the specified image.
    #
    # @param image The name of the docker image.
    #
    # @return None
    def __fetchImage(self, image):
        _checkedDockerCommand(["pull", image])

    ##
    # @brief Start an image.
    #
    # @param dockerImage The name of the image to start.
    # @param env The environment variables to set.
    #
    # @return The started container.
    def start(self, dockerImage, env=None):
        self.__fetchImage(dockerImage)
        return DockerContainer(imageName=dockerImage, useLXC=self._useLXC,
                               environment=env)

    ##
    # @brief Close the container (actualyl just delete the image).
    #
    # @param container The container.
    #
    # @return None
    def stop(self, container):
        container.stop()
