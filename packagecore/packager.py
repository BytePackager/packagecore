##
# @file packager.py
# @brief The top-level Packager class for orchestrating the package builds.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-03

import shutil
import os
import traceback

from .docker import Docker
from .pkgbuild import PkgBuild
from .dpkg import DebianPackage
from .rpm import RPM
from .distributions import DATA as BUILDS
from .scriptfile import generateScript
from .configparser import parse


class UnknownPackageTypeError(Exception):
    pass


class PackageNotFoundError(Exception):
    pass


class Packager:
    ##
    # @brief Create a packager object.
    #
    # @param conf The configuration to use.
    # @param outputDir The directory to output packages into.
    # @param srcDir The directory containing the projects source.
    # @param version The version of packages to generate.
    # @param release The release number.
    # @param distributions The distributions to build a package for.
    #
    # @return The new Packager.
    def __init__(self, conf, srcDir, outputDir, version, release,
                 distributions=None, environment=None):
        self._outputDir = outputDir
        self._srcDir = srcDir

        if not environment:
            environment = {}
        self._environment = environment

        if not os.path.exists(self._outputDir):
            os.makedirs(self._outputDir)

        builds = parse(conf=conf, version=version, release=release)

        if distributions:
            self._queue = []

            for distribution in distributions:
                if distribution in builds.keys():
                    self._queue.append(builds[distribution])
                else:
                    raise PackageNotFoundError("No '%s' listed in configuration." %
                                               distribution)
        else:
            self._queue = builds.values()

        self._docker = Docker()

    ##
    # @brief Build a given package.
    #
    # @param job The job associated with the package.
    # @param recipe The recipe object for the package type.
    # @param packageNameFormat The format of the package name.
    # @param imageName The name of the docker image to use.
    #
    # @return None
    def _build(self, job, recipe, packageNameFormat, imageName):
        tmpfile = os.path.join("/tmp", recipe.getName())
        name = packageNameFormat.format(
            name=job.name, version=job.version,
            release=job.releaseNum, arch=recipe.getArch())
        outfile = os.path.join(self._outputDir, name)

        # build the package
        container = self._docker.start(imageName, env=self._environment)

        print("Using shared directory '%s' and source directory '%s'." %
              (container.getSharedDir(), container.getSourceDir()))

        try:
            # copy in source -- we must be in the source directory
            container.copySource(self._srcDir)

            # run the 'pre' commands in the container
            preCmdFile = os.path.join(
                container.getSharedDir(), ".preCmds")
            generateScript(preCmdFile, job.preCompileCommands)

            recipe.prep(container)
            recipe.build(container)

            # copy out finished package
            shutil.copy(
                os.path.join(container.getSharedDir(),
                             recipe.getName()),
                tmpfile)
        finally:
            container.stop()

        # move the package to the current directory
        shutil.move(tmpfile, outfile)

        # spawn a new docker container
        container = self._docker.start(imageName, env=self._environment)
        try:
            # copy in the package for installation
            dstFile = os.path.join(
                container.getSharedDir(), recipe.getName())
            shutil.copy(outfile, dstFile)
            recipe.install(container)

            container.executeScript(job.testInstallCommands,
                                    {"BP_PACKAGE_FILE": dstFile})
        finally:
            container.stop()

    ##
    # @brief Build each package.
    #
    # @return None
    def run(self):
        success = True
        if not self._queue:
            print("No packages to build.")
            success = False
        for job in self._queue:
            osName = job.osName
            build = BUILDS[osName]
            if not job.container is None:
                build["dockerImage"] = job.container
            elif not "dockerImage" in build or build["dockerImage"] is None:
                print("??????????????????????????????????????????????????????")
                print("? A docker container must be specified for '%s' in "
                      % job.osName)
                print("? your .yaml file using the 'container' key.")
                print("? Distributions without official containers in ")
                print("? Dockerhub now require a user specified container.")
                print("? You should only use trusted containers, as a")
                print("? maliciously configured container could be use to")
                print("? compromise your machine as well as modify the")
                print("? packages you are building.")
                print("?")
                print("? For an example of how to specify a container in a ")
                print("? .yaml filex:")
                print("? ```")
                print("? ...")
                print("? %s:" % job.osName)
                print("?   ...")
                print("?   container: example.com/myuser/my-arch-linux:latest")
                print("? ```")
                print("??????????????????????????????????????????????????????")
                raise RuntimeError("Bad configuration file.")

            nameFormat = build["formatString"]
            pkgType = build["packageType"]
            if pkgType == "pkgbuild":
                recipe = PkgBuild(job)
            elif pkgType == "debian":
                recipe = DebianPackage(job)
            elif pkgType == "rpm-dnf":
                recipe = RPM(job, packageManager="dnf")
            elif pkgType == "rpm-yum":
                recipe = RPM(job, packageManager="yum")
            elif pkgType == "rpm-zypper":
                recipe = RPM(job, packageManager="zypper")
            else:
                raise UnknownPackageTypeError(
                    "Unknown packaging type: %s" % pkgType)

            try:
                print("Building package for %s: %s" % (osName, str(job)))
                self._build(job, recipe, packageNameFormat=nameFormat,
                            imageName=build["dockerImage"])

                print()
                print("###########################################################")
                print("# Successfully built package for '%s'." % osName)
                print("###########################################################")
                print()
            # we want to catch virtually all exceptions here
            # pylint: disable=broad-except
            except Exception:
                print()
                print("###########################################################")
                print("# Failed to build package for '%s'." % osName)
                print("###########################################################")
                print(traceback.format_exc())
                print("###########################################################")
                print()
                success = False
        return success
