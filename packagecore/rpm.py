##
# @file rpm.py
# @brief Class for generating RPMs.
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
from .docker import DockerError


RPM_ZYPPER = "zypper"
RPM_DNF = "dnf"
RPM_YUM = "yum"


class InvalidStateError(Exception):
    pass


class UnknownPackageManagerError(Exception):
    pass


def sanitize(version):
    return re.sub(r'[/\s:-]', "_", version)


class RPM:
    ##
    # @brief Create a new rpm object.
    #
    # @param data Information about the package to build.
    # @param packageManager The package manager to use.
    #
    # @return The new object.
    def __init__(self, data, packageManager):
        self._data = data
        self._sanitizedVersion = sanitize(data.version)
        self._specFile = None
        self._packageManager = packageManager

    ##
    # @brief RPMs require a complete list of all files installed, so this
    # function unpacks the RPM, reads the list of all installed files, and writes
    # that back to the spec file.
    #
    # @param container
    #
    # @return None
    def __fixFiles(self, container):
        # generate script
        filename = os.path.join(container.getSourceDir(),
                                ".bytepackager_fixrpm.sh")

        script = \
            """
RPM="${1}"

FSFILES="/tmp/.fsfiles"
PKFILES="/tmp/.pkfiles"

NEWFILES="/tmp/.newfiles"

which dnf && RPMQ="dnf repoquery" || RPMQ="repoquery"

rpm -ql filesystem | grep -v 'Last metadata expiration check' | sort > "${FSFILES}"
rpm -qlp "${RPM}" | sort > "${PKFILES}"

comm -23 "${PKFILES}" "${FSFILES}" | sort -u > "${NEWFILES}"

OUTPUT="$(rpmrebuild -p --change-spec-files="cat ${NEWFILES}" "${RPM}")"

OUTRPM="${OUTPUT#result: }"

cp "${OUTRPM}" "${RPM}"
"""

        generateScript(filename, script)

        print("Setting list of installed files in RPM.")
        container.execute([filename,
                           os.path.join(container.getSharedDir(), self.getName())])

    ##
    # @brief Get the name of the spec file that will be generated.
    #
    # @return The name/path.
    def getSpecFileName(self):
        return self._specFile

    ##
    # @brief Write a spec file for building the rpm.
    #
    # @param container The container to build in.
    #
    # @return None
    def generateSpecFile(self, container):
        if self._specFile is None:
            raise InvalidStateError("Spec file has not been set yet. Make sure "
                                    "you call prep() first.")
        buildEnv = BuildVariables(destDir="%{buildroot}",
                                  sourceDir=container.getSourceDir())

        with open(self._specFile, "w") as specFile:
            specFile.write("%%define _build_name_fmt %s\n" % self.getName())
            specFile.write("%%define _rpmdir %s\n" % container.getSharedDir())
            specFile.write("\n")
            specFile.write("Name: %s\n" % self._data.name)
            specFile.write("Version: %s\n" % self._sanitizedVersion)
            specFile.write("Release: %d%%{?dist}\n" % self._data.releaseNum)
            specFile.write("Summary: %s\n" % self._data.summary)
            specFile.write("Group: other\n")
            specFile.write("License: %s\n" % self._data.license)
            for dep in self._data.runDeps:
                specFile.write("Requires: %s\n" % dep)
            for dep in self._data.buildDeps:
                specFile.write("BuildRequires: %s\n" % dep)
            if not self._data.maintainer is None and \
                    self._data.maintainer != "":
                specFile.write("Packager: %s\n" % self._data.maintainer)
            if not self._data.homepage is None and \
                    self._data.homepage != "":
                specFile.write("URL: %s\n" % self._data.homepage)
            specFile.write("\n")
            specFile.write("%description\n")
            specFile.write("\n")
            specFile.write("%build\n")
            buildEnv.write(specFile)
            specFile.write("cd \"%s\"\n" % container.getSourceDir())
            specFile.write(self._data.compileCommands)
            specFile.write("\n")
            specFile.write("%install\n")
            buildEnv.write(specFile)
            specFile.write("cd \"%s\"\n" % container.getSourceDir())
            specFile.write(self._data.installCommands)
            specFile.write("\n")

            if self._data.postInstallCommands:
                specFile.write("%post\n")
                specFile.write("""
if [[ "${1}" == "1" ]]; then
  BP_UPGRADE="false"
else
  BP_UPGRADE="true"
fi
        """)
                specFile.write(self._data.postInstallCommands)
                specFile.write("\n")

            specFile.write("%files\n")
            specFile.write("/\n")
            specFile.write("\n")

        with open(self._specFile, "r") as specFile:
            print("Using specfile:{")
            print(specFile.read())
            print("}")

    ##
    # @brief Do preparation steps before building (e.g., generate files).
    #
    # @param container The container to build in.
    #
    # @return None
    def prep(self, container):
        # install necessary utilities

        # will need to be back ported for centos
        if self._packageManager == RPM_YUM:
            container.execute(["/usr/bin/yum", "install", "-y", "yum-utils",
                               "rpm-build", "which", "make"])
            # try to install rpmrebuild -- if it fails, add epel and try again
            try:
                container.execute(
                    ["/usr/bin/yum", "install", "-y", "rpmrebuild"])
            except DockerError:
                container.execute(
                    ["/usr/bin/yum", "install", "-y", "epel-release"])
                container.execute(
                    ["/usr/bin/yum-config-manager", "--enable", "epel"])
                container.execute(
                    ["/usr/bin/yum", "install", "-y", "rpmrebuild"])
        elif self._packageManager == RPM_DNF:
            container.execute(["/usr/bin/dnf", "install", "-y",
                               "dnf-command(repoquery)", "rpm-build", "rpmrebuild",
                               "dnf-command(builddep)", "which", "make"])
        elif self._packageManager == RPM_ZYPPER:
            container.execute(["/usr/bin/zypper", "in", "-y", "rpmrebuild",
                               "which", "make"])
        else:
            raise UnknownPackageManagerError("Unknown packager manager "
                                             "'%s'." % self._packageManager)

        self._specFile = os.path.join(container.getSharedDir(), "pkg.spec")
        self.generateSpecFile(container)

    ##
    # @brief Build the debian package. Once the package is finished building, it
    # reside in /tmp/ on the chroot.
    #
    # @param container The container to build in.
    #
    # @return None
    def build(self, container):
        # will need to be back ported for centos
        if self._packageManager == RPM_YUM:
            container.execute(["/usr/bin/yum-builddep", "-y", self._specFile])
        elif self._packageManager == RPM_DNF:
            container.execute(
                ["/usr/bin/dnf", "builddep", "-y", self._specFile])
        elif self._packageManager == RPM_ZYPPER:
            # there is no buildep functionality of opensuse -- so we'll install by
            # hand
            container.execute(["/usr/bin/zypper", "in", "-y"] +
                              self._data.buildDeps)
        else:
            raise UnknownPackageManagerError("Unknown packager manager "
                                             "'%s'." % self._packageManager)

        # sudo
        container.execute(["rpmbuild",
                           "--define=_topdir %s" % container.getSharedDir(), "-bb",
                           self._specFile])

        self.__fixFiles(container)

    ##
    # @brief Install the package.
    #
    # @param container The container to install in.
    #
    # @return None
    def install(self, container):
        # test package
        if self._packageManager == RPM_YUM:
            container.execute(["yum", "install", "-y",
                               os.path.join(container.getSharedDir(), self.getName())])
        elif self._packageManager == RPM_DNF:
            container.execute(["dnf", "install", "-y",
                               os.path.join(container.getSharedDir(), self.getName())])
        elif self._packageManager == RPM_ZYPPER:
            # using the "--no-gpg-checks" is undesirable as we only want to
            # allow this package ot be unsigned, but we want its dependencies
            # to be signed. However, we're installing on a throw away container
            # and not copying anything out, so the security risk is not large
            # (though in theory if someone was able to get a malicious version
            # of a dependency installed that executed code that was able to
            # break out of the container, this would be an issue).
            container.execute(["zypper", "--no-gpg-checks", "in", "-y",
                               os.path.join(container.getSharedDir(), self.getName())])
        else:
            raise UnknownPackageManagerError("Unknown packager manager "
                                             "'%s'." % self._packageManager)

    ##
    # @brief Get the full package name.
    #
    # @return The full package name.
    def getName(self):
        return "%s-%s-%d.rpm" % (self._data.name, self._sanitizedVersion,
                                 self._data.releaseNum)

    ##
    # @brief Get the architecture field for the package name.
    #
    # @return The architecture name (e.g., x86_64).
    def getArch(self):
        bits = platform.architecture()[0]
        # need to add arm support -- ticket #103
        if bits == "64bit":
            return "x86_64"
        else:
            return "i686"
