##
# @file dpkg.py
# @brief Class for creating debian packages.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-26


import os
import os.path
import re
import platform

from .buildvariables import BuildVariables
from .scriptfile import generateScript


def _sanitize(version):
    version = version.lower()
    version = re.sub(r'[/\s_]', "-", version)
    return version


def _makeDir(path):
    try:
        os.makedirs(path, 0o755)
    except FileExistsError:
        pass


class DebianPackage:
    ##
    # @brief Create a new debian package object.
    #
    # @param build Information about the package to build.
    #
    # @return The new object.
    def __init__(self, data):
        self._data = data
        self._sanitizedVersion = _sanitize(data.version)

        self._pkgBuildDir = None
        self._pkgInfoDir = None

    ##
    # @brief Write a control file for building the debian package.
    #
    # @return None
    def generateControlFile(self):
        ctrlFilePath = os.path.join(self._pkgInfoDir, "control")
        with open(ctrlFilePath, "w") as ctrlFile:
            ctrlFile.write("Source: %s\n" % self._data.name)
            ctrlFile.write("Version: %s-%d\n" % (self._sanitizedVersion,
                                                 self._data.releaseNum))
            ctrlFile.write("Section: unknown\n")
            ctrlFile.write("Priority: optional\n")
            ctrlFile.write("Maintainer: %s\n" % self._data.maintainer)
            ctrlFile.write("Build-Depends: %s\n" %
                           (", ".join(self._data.buildDeps)))
            ctrlFile.write("Standards-Version: 3.9.6\n")
            ctrlFile.write("Homepage: %s\n" % self._data.homepage)
            ctrlFile.write("Package: %s\n" % self._data.name)
            ctrlFile.write("Architecture: amd64\n")
            ctrlFile.write("Depends: %s\n" % (", ".join(self._data.runDeps)))
            ctrlFile.write("Description: %s\n" % self._data.summary)

    ##
    # @brief Write a copyright file for building the debian package.
    #
    # @return None
    def generateCopyrightFile(self):
        copyFilePath = os.path.join(self._pkgInfoDir, "copyright")
        with open(copyFilePath, "w") as copyFile:
            copyFile.write("Format: http://www.debian.org/doc/packaging-manuals/"
                           "copyright-format/1.0/\n")
            copyFile.write("License: %s\n" % self._data.license)

    ##
    # @brief Write a 'postinst' (the post installation script) for the package.
    #
    # @return None
    def generatePostInstallFile(self):
        postFilePath = os.path.join(self._pkgInfoDir, "postinst")
        # create post install script
        if self._data.postInstallCommands:
            generateScript(postFilePath,
                           """
if [[ -z "${2}" ]]; then
  BP_UPGRADE="false"
else
  BP_UPGRADE="true"
fi

%s
          """ % self._data.postInstallCommands)

    ##
    # @brief Prepare to build package.
    #
    # @param container The container to build in.
    #
    # @return None
    def prep(self, container):
        # setup internal file structure
        self._pkgBuildDir = os.path.join(container.getSharedDir(),
                                         "%s-%s" % (self._data.name, self._sanitizedVersion))
        self._pkgInfoDir = os.path.join(self._pkgBuildDir, "DEBIAN")
        _makeDir(self._pkgBuildDir)
        _makeDir(self._pkgInfoDir)

        # generate neccesary files
        self.generateControlFile()
        self.generateCopyrightFile()
        self.generatePostInstallFile()

    ##
    # @brief Build the debian package. It will reside in /tmp/ on the chroot.
    #
    # @param container The container to build in.
    #
    # @return None
    def build(self, container):
        # set timezone in container so tzdata can configure non-interactively
        container.execute(
            ["/bin/bash", "-c", "echo 'Etc/UTC' > /etc/timezone"])
        container.execute(
            ["/bin/bash", "-c", "ln -f -s /usr/share/zoneinfo/Etc/UTC /etc/localtime"])

        # install build deps
        container.execute(["/usr/bin/apt-get", "update", "-qy"])
        if self._data.buildDeps:
            container.executeScript(
                "/usr/bin/apt-get install -qy %s" % (
                    " ".join(self._data.buildDeps)),
                {"DEBIAN_FRONTEND": "noninteractive",
                 "DEBCONF_NONINTERACTIVE_SEEN": "true"})

        # create build script
        buildScriptFilename = ".bytepackager_build.sh"
        buildScriptFilenameLocal = os.path.join(container.getSourceDir(),
                                                buildScriptFilename)

        destDir = self._pkgBuildDir
        buildEnv = BuildVariables(destDir=destDir,
                                  sourceDir=container.getSourceDir())

        generateScript(buildScriptFilenameLocal,
                       ("cd %s\n" % container.getSourceDir()) +
                       self._data.compileCommands, buildEnv.generate())

        # create install script
        installScriptFilename = ".bytepackager_install.sh"
        installScriptFilenameLocal = \
            os.path.join(container.getSourceDir(), installScriptFilename)

        generateScript(installScriptFilenameLocal,
                       ("cd %s\n" % container.getSourceDir()) +
                       self._data.installCommands, buildEnv.generate())

        # perform build
        container.execute(buildScriptFilenameLocal)

        # perform installation
        container.execute(installScriptFilenameLocal)

        filename = self.getName()
        path = os.path.join(container.getSharedDir(), filename)

        # build package
        container.execute(["/usr/bin/dpkg-deb", "--build", self._pkgBuildDir,
                           path])

    ##
    # @brief Install the generated package.
    #
    # @param container The container to install the package in.
    #
    # @return None
    def install(self, container):
        # set timezone in container so tzdata can configure non-interactively
        container.execute(
            ["/bin/bash", "-c", "echo 'Etc/UTC' > /etc/timezone"])
        container.execute(
            ["/bin/bash", "-c", "ln -f -s /usr/share/zoneinfo/Etc/UTC /etc/localtime"])

        # manually install dependencies
        container.execute(["/usr/bin/apt-get", "update", "-qy"])
        container.executeScript(
            "/usr/bin/apt-get install -qy %s" % (" ".join(self._data.runDeps)),
            {"DEBIAN_FRONTEND": "noninteractive",
             "DEBCONF_NONINTERACTIVE_SEEN": "true"})

        # test package
        container.execute(["/usr/bin/dpkg", "-i",
                           os.path.join(container.getSharedDir(), self.getName())])

    ##
    # @brief Get the full package name.
    #
    # @return The full package name.
    def getName(self):
        return "%s_%s-%d_amd64.deb" % (self._data.name, self._sanitizedVersion,
                                       self._data.releaseNum)

    ##
    # @brief Get the architecture field for the package name.
    #
    # @return The architecture name (e.g., x86_64).
    def getArch(self):
        bits = platform.architecture()[0]
        # In the future this will need to work with arm -- see ticket #103
        if bits == "64bit":
            return "amd64"
        else:
            return "i386"
