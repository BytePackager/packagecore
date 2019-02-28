##
# @file builddata.py
# @brief Struct for holding build information.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-29


def generateMockData():
    data = BuildData("mypackage", "1.2.3", 2, "centos7", "",
                     "./configure\nmake", "make install", "adduser -m test", "ls")
    data.license = "MIT"
    data.homepage = "www.test.com"
    data.summary = "A really important and good package"
    data.maintainer = "me"
    data.buildDeps = ["cmake", "gcc"]
    data.runDeps = ["openssl", "glibc", "libwxgtk"]
    data.container = None

    return data

# some day it may be worth while to decompose this a bit more
#pylint: disable=too-many-instance-attributes


class BuildData:
    def __init__(self, name, version, releaseNum, osName, preCompileCommands,
                 compileCommands, installCommands, postInstallCommands,
                 testInstallCommands):
        # we only want lower-case package names.
        self.name = name.lower()
        self.version = version
        self.releaseNum = releaseNum
        self.maintainer = ""
        self.license = "Custom"
        self.homepage = ""
        self.summary = "none"
        self.osName = osName
        self.buildDeps = []
        self.runDeps = []
        self.preCompileCommands = preCompileCommands
        self.compileCommands = compileCommands
        self.installCommands = installCommands
        self.postInstallCommands = postInstallCommands
        self.testInstallCommands = testInstallCommands
        self.container = None

    def __str__(self):
        return \
            """
      name: %s
      version: %s
      releaseNum: %d
      maintainer: %s
      license: %s
      homepage: %s
      summary: %s
      os: %s
      buildDeps: %s
      runDeps: %s
      preCompileCommands: %s
      compileCommands: %s
      installCommands: %s
      postInstallCommands: %s
      testInstallCommands: %s
      container: %s
      """ % (self.name, self.version, self.releaseNum, self.maintainer,
             self.license, self.homepage, self.summary, self.osName, self.buildDeps,
             self.runDeps, self.preCompileCommands, self.compileCommands,
             self.installCommands, self.postInstallCommands,
             self.testInstallCommands, self.container)
