##
# @file pkgbuild.py
# @brief Class for generating .pkg packages.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-28


import os
import os.path
import tarfile
import re
import platform

from .buildvariables import BuildVariables
from .scriptfile import generateScript


# it's important we don't have trailing slashes
SYMLINKS = {
    "/lib": "/usr/lib",
    "/bin": "/usr/bin",
    "/sbin": "/usr/bin",
    "/lib64": "/usr/lib",
    "/usr/lib64": "/usr/lib",
    "/usr/sbin": "/usr/bin"
}


def _sanitize(version):
    return re.sub(r'[/\s:-]', "_", version)


def _makeDir(path):
    try:
        os.makedirs(path, 0o700)
    except FileExistsError:
        pass


class PkgBuild:
    ##
    # @brief Create a new package object.
    #
    # @param build Information about the package to build.
    #
    # @return The new object.
    def __init__(self, data):
        self._data = data
        self._sanitizedVersion = _sanitize(data.version)

        # setup internal file structure
        self._pkgBuildDir = None
        self._pkgTar = "pkg.tar"

    ##
    # @brief Create a tarball of the source code.
    #
    # @param container The container to build in.
    #
    # @return None
    def makeSrcTar(self, container):
        # this function violates the chroot encapsulation quite badly...
        filename = os.path.join(self._pkgBuildDir, self._pkgTar)
        if filename.endswith(".tar"):
            mode = "w"
        elif filename.endswith(".tar.gz"):
            mode = "w:gz"
        else:
            raise Exception("Unknown tar format '%s'" % filename)
        # make tarball from source
        with tarfile.open(filename, mode) as tar:
            tar.add(container.getSourceDir(),
                    arcname=os.path.basename(container.getSourceDir()))

    ##
    # @brief Write a control file for building the debian package.
    #
    # @return None
    def generatePKGBUILDFile(self, container):
        # while it doesn't make sense to break up the writing of the PKGBUILD
        # file, it we could move the special root construction to another
        # function.
        #pylint: disable=too-many-statements
        buildEnv = BuildVariables(destDir="$pkgdir",
                                  sourceDir=container.getSourceDir())

        # assemble PKGBUILD
        with open(os.path.join(self._pkgBuildDir, "PKGBUILD"), "w") as pkgFile:
            pkgFile.write("pkgname=%s\n" % self._data.name)
            pkgFile.write("pkgver=%s\n" % self._sanitizedVersion)
            pkgFile.write("pkgrel=%d\n" % self._data.releaseNum)
            pkgFile.write("epoch=\n")
            pkgFile.write("pkgdesc=\"%s\"\n" %
                          self._data.summary.replace('"', "'"))
            pkgFile.write("arch=(\"x86_64\")\n")
            pkgFile.write("url=\"%s\"\n" % self._data.homepage)
            pkgFile.write("license=('%s')\n" % self._data.license)
            pkgFile.write("groups=()\n")
            pkgFile.write("depends=(\n")
            for dep in self._data.runDeps:
                pkgFile.write("  %s\n" % dep)
            pkgFile.write(")\n")
            pkgFile.write("makedepends=(\n")
            for dep in self._data.buildDeps:
                pkgFile.write("  %s\n" % dep)
            pkgFile.write(")\n")
            pkgFile.write("checkdepends=()\n")
            pkgFile.write("optdepends=()\n")
            pkgFile.write("provides=()\n")
            pkgFile.write("conflicts=()\n")
            pkgFile.write("replaces=()\n")
            pkgFile.write("backup=()\n")
            pkgFile.write("options=()\n")
            if self._data.postInstallCommands:
                instFileName = "%s.install" % self._data.name
                pkgFile.write("install=%s\n" % instFileName)
                # let users differentiate between post install and post upgrade
                generateScript(os.path.join(self._pkgBuildDir, instFileName),
                               """
post_install() {
BP_UPGRADE="false"
%s
}
post_upgrade() {
BP_UPGRADE="true"
%s
}
          """ % (self._data.postInstallCommands,
                 self._data.postInstallCommands))
            else:
                pkgFile.write("install=\n")
            pkgFile.write("changelog=\n")
            pkgFile.write("source=(\"%s\")\n" % self._pkgTar)
            pkgFile.write("\n")

            # write compile commands
            pkgFile.write("build() {\n")
            buildEnv.write(pkgFile)
            pkgFile.write("cd %s\n" % container.getSourceDir())
            pkgFile.write(self._data.compileCommands)
            pkgFile.write("\n")
            pkgFile.write("}\n")
            pkgFile.write("\n")

            # write install commands
            pkgFile.write("package() {\n")
            buildEnv.write(pkgFile)

            # arc uses many symlink in filesystem, so we'll create them to let things
            # get installed in the right locations and remove them
            pkgFile.write("mkdir -p \"${BP_DESTDIR}/usr\"\n")
            pkgFile.write("mkdir -p \"${BP_DESTDIR}/usr/lib\"\n")
            pkgFile.write("mkdir -p \"${BP_DESTDIR}/usr/bin\"\n")
            for link, dest in SYMLINKS.items():
                pkgFile.write("ln -s \"${BP_DESTDIR}/%s\" \"${BP_DESTDIR}/%s\"\n" %
                              (dest, link))

            pkgFile.write("cd %s\n" % container.getSourceDir())
            pkgFile.write(self._data.installCommands)
            pkgFile.write("\n")

            # remove symlinks
            for link, dest in SYMLINKS.items():
                pkgFile.write("rm -f \"${BP_DESTDIR}/%s\"\n" % link)

            # remove /usr/lib and /usr/bin if no files placed in them
            pkgFile.write("test \"$(ls -A \"${BP_DESTDIR}/usr/bin\")\" || ")
            pkgFile.write("  rmdir \"${BP_DESTDIR}/usr/bin\"\n")
            pkgFile.write("test \"$(ls -A \"${BP_DESTDIR}/usr/lib\")\" || ")
            pkgFile.write("  rmdir \"${BP_DESTDIR}/usr/lib\"\n")
            pkgFile.write("test \"$(ls -A \"${BP_DESTDIR}/usr\")\" || ")
            pkgFile.write("  rmdir \"${BP_DESTDIR}/usr\"\n")

            pkgFile.write("}\n")
            pkgFile.write("\n")

    ##
    # @brief Prepare for building.
    #
    # @return None
    def prep(self, container):
        container.execute(["pacman", "-Syy", "--noconfirm", "sudo", "binutils",
                           "fakeroot"])
        uid = os.getuid()
        if uid == 0:
            # if we're running as root, make up a user
            uid = 1000
        container.execute(["useradd", "-m", "-u", str(uid), "packagecore"])
        container.execute(["/bin/bash", "-c",
                           "echo 'packagecore ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers"])
        # create our working directory
        self._pkgBuildDir = os.path.join(container.getSharedDir(),
                                         "arch-pkg")
        _makeDir(self._pkgBuildDir)

        self.generatePKGBUILDFile(container)

    ##
    # @brief Build the arch package.
    #
    # @param container The container to build in.
    #
    # @return None
    def build(self, container):
        self.makeSrcTar(container)

        # update keyring
        container.execute(["/usr/bin/pacman", "--noconfirm", "-S", "-yy",
                           "archlinux-keyring"])
        # update image
        container.execute(["/usr/bin/pacman", "--noconfirm", "-Su", "-yy"])

        # create a custom makepkg.conf
        makePkgConfOrig = os.path.join(
            container.getSharedDir(), "makepkg.conf.orig")
        container.execute(["cp", "/etc/makepkg.conf", makePkgConfOrig])
        with open(makePkgConfOrig, "r") as confFile:
            content = confFile.read()

        makePkgConf = os.path.join(container.getSharedDir(), "makepkg.conf")
        with open(makePkgConf, "w") as confFile:
            confFile.write(content)
            confFile.write("\n")
            confFile.write("PKGDEST=\"%s\"\n" % container.getSharedDir())
            confFile.write("SRCDEST=\"%s\"\n" % container.getSharedDir())
            confFile.write("BUILDDIR=\"%s\"\n" % container.getSharedDir())

        # execute makepkg -sri

        # docker doesn't let us change the working directory using `exec`, so we
        # need to use a shell
        container.execute(["/bin/bash", "-c",
                           ("pushd '%s' && sudo -u packagecore makepkg --skipinteg --noconfirm "
                            "--noprogressbar -sr --config='%s' PACKAGER='%s' && popd") %
                           (self._pkgBuildDir, makePkgConf, self._data.maintainer)])

    ##
    # @brief Install the generated package.
    #
    # @param container The container to install the package in.
    #
    # @return None
    def install(self, container):
        # test package
        # sudo
        container.execute(["/usr/bin/pacman", "--noconfirm", "-Syy"])
        container.execute(["/usr/bin/pacman", "--noconfirm", "-U",
                           os.path.join(container.getSharedDir(), self.getName())])

    ##
    # @brief Get the full package name.
    #
    # @return The full package name.
    def getName(self):
        return "%s-%s-%d-x86_64.pkg.tar.xz" % \
            (self._data.name, self._sanitizedVersion, self._data.releaseNum)

    ##
    # @brief Get the architecture field for the package name.
    #
    # @return The architecture name (e.g., x86_64).
    def getArch(self):
        bits = platform.architecture()[0]
        # Need to work with arm - ticket #103
        if bits == "64bit":
            return "x86_64"
        else:
            return "i686"
